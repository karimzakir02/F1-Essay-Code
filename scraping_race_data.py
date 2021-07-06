"""
    This script contains the code for scraping the data for F1 races from the
    official Formula 1 Website. I am only going to be scraping the data from
    the third practice session and the race itself, since my paper focuses on
    these particular sessions. Additionally, I will only be scraping data from
    the beginning of the turbo hybrid era (2014) until 2019 inclusive.

    The 2014-2018 data will be used for analysis, while the 2019 data will
    be used in order to evaluate my predictions models; this is why the data
    for the two time periods is stored in separate folders.

    If you have any suggestions on how I can improve this code, feel free to
    open an issue on GitHub. I would love to hear your insight!
"""
from abc import ABC, abstractmethod
import requests
import pandas as pd
import csv
import aiohttp
import asyncio
import concurrent
import threading

# Constants:
INPUT_PATH = "data/links.csv"
OUTPUT_PATH = "data"


class AbstractScraper(ABC):

    def __init__(self, path_to_links, output_path):
        self.links = []
        with open(path_to_links, "r") as f:
            reader = csv.reader(f)

            for row in reader:
                self.links.append(row[0])

        self.race_count = []
        for link in self.links:
            # The links contain the race number, which I am finding in this
            # for loop. The reason why I am doing this and not simply
            # creating a range is because the race numbers are not strictly
            # consistent on the website for an unknown reason.
            try:
                race_number_pos = link.find("races/") + len("races/")
                race_number_str = link[race_number_pos:race_number_pos + 4]
                race_number = int(race_number_str)
            except ValueError:
                race_number_pos = link.find("races/") + len("races/")
                race_number_str = link[race_number_pos:race_number_pos + 3]
                race_number = int(race_number_str)
            self.race_count.append(race_number)

        self.output_path = output_path
        self.extensions = ("practice-3.html", "race-result.html")

        # Positions which will not be considered:
        self.invalid_positions = {"NC", "DQ", "EX"}

    @abstractmethod
    def scrape():
        # To be implemented in the child classes
        pass

    def _process_data(self, fp3_df, race_df):
        # The function processes the data to only contain what that we require
        fp3_df = fp3_df[["Driver", "Pos"]]
        fp3_df = fp3_df[~fp3_df["Pos"].isin(self.invalid_positions)]
        fp3_df["Pos"] = fp3_df["Pos"].astype(int)

        race_df = race_df[["Driver", "Pos"]]
        race_df = race_df[~race_df["Pos"].isin(self.invalid_positions)]
        race_df["Pos"] = race_df["Pos"].astype(int)

        fp3_race = fp3_df.merge(race_df, on="Driver")
        fp3_race.columns = ["driver", "fp3_pos", "race_pos"]

        fp3_race = fp3_race[(fp3_race["fp3_pos"] <= 20) &
                            (fp3_race["race_pos"] <= 20)]
        # The reason why I am only considering the Top 20 positions is because
        # there were only 20 racers in the 2019 season.
        return fp3_race


class StandardScraper(AbstractScraper):
    """
        The StandardScraper class provides the interface for simple scraping.
        It takes the longest amount of time, because it waits for a response
        from each link without moving on.
    """

    def scrape(self):
        session = requests.Session()
        for link, race_number in zip(self.links, self.race_count):
            fp3_response = session.get(link + self.extensions[0])
            race_response = session.get(link + self.extensions[1])

            fp3_df = pd.read_html(fp3_response.content)[0]
            race_df = pd.read_html(race_response.content)[0]

            processed_data = self._process_data(fp3_df, race_df)
            folder_path = "2014-2018"
            if race_number >= 1000:
                # The 1000th race denoted the beginning of the 2019 season
                folder_path = "2019"
            save_path = f"{self.output_path}/{folder_path}/{race_number}.csv"
            processed_data.to_csv(save_path, index=False)

        print("Complete!")


class AsyncScraper(AbstractScraper):

    """
        The AsycnScraper class provides the interface for asynchrous scraping.
        It uses asyncio and aiohttp to asynchrosly scrape the provided links.
    """

    def scrape(self):
        asyncio.get_event_loop().run_until_complete(self._scrape())

    async def _scrape(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for link, race_number in zip(self.links, self.race_count):
                # Queueing the tasks
                task = asyncio.ensure_future(self._get_data(session, link,
                                                            race_number))
                tasks.append(task)
            await asyncio.gather(*tasks)

    async def _get_data(self, session, link, race_number):
        async with session.get(link + self.extensions[0]) as response:
            fp3_data = await response.read()

        async with session.get(link + self.extensions[1]) as response:
            race_data = await response.read()

        fp3_df = pd.read_html(fp3_data)[0]
        race_df = pd.read_html(race_data)[0]

        processed_data = self._process_data(fp3_df, race_df)
        if race_number >= 1000:
            folder_path = "2019"
        else:
            folder_path = "2014-2018"
        save_path = f"{self.output_path}/{folder_path}/{race_number}.csv"
        processed_data.to_csv(save_path, index=False)


class ThreadingScraper(AbstractScraper):

    """
        The ThreadingScraper class provides the interface to concurrently
        scrape the data using threading. It uses the concurrent and threading
        libraries.
    """

    def __init__(self, path_to_links, output_path):
        super().__init__(path_to_links, output_path)
        # Required variable to ensure thread-safety:
        self.thread_local = threading.local()

    def scrape(self):
        # The max_workers can be played around with to find the most optimal
        # amount of workers for this task.
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self._get_data, self.links, self.race_count)

    def _get_data(self, link, race_number):
        session = self._get_thread_session()
        with session.get(link + self.extensions[0]) as response:
            fp3_response = response
        with session.get(link + self.extensions[1]) as response:
            race_response = response

        fp3_df = pd.read_html(fp3_response.content)[0]
        race_df = pd.read_html(race_response.content)[0]

        processed_data = self._process_data(fp3_df, race_df)

        if race_number >= 1000:
            folder_path = "2019"
        else:
            folder_path = "2014-2018"
        save_path = f"{self.output_path}/{folder_path}/{race_number}.csv"
        processed_data.to_csv(save_path, index=False)

    def _get_thread_session(self):
        # Each thread has its own session to make sure that we do not hit any
        # errors
        if not hasattr(self.thread_local, "session"):
            self.thread_local.session = requests.Session()
        return self.thread_local.session


if __name__ == '__main__':
    # Start the scrapers here:
    scraper = AsyncScraper(INPUT_PATH, OUTPUT_PATH)
    scraper.scrape()
