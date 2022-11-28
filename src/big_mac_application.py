import pathlib

import constants
from src.core.presentation.main_menu import MainMenu
from src.core.presentation.main_menu_controller import MainMenuController
from src.features.price_loading.data.data_sources.csv_data_source import CsvDataSource
from src.features.price_loading.data.data_sources.utils.csv_file_reader import CsvFileReader
from src.features.price_loading.data.repositories.mappers.csv_price_mapper import CsvPriceMapper
from src.features.price_loading.data.repositories.price_repository_impl import PriceRepositoryImpl
from src.features.price_loading.domain.use_cases.load_prices_use_case import LoadPricesUseCase
from src.features.price_loading.repository.price_repository import PriceRepository
from src.features.statistics.domain.use_cases.calculate_average_price_per_country_use_case import \
    CalculateAveragePricePerCountryUseCase
from src.features.statistics.domain.use_cases.calculate_cheapest_country_use_case import CalculateCheapestCountryUseCase
from src.features.statistics.domain.use_cases.calculate_most_expensive_country_use_case import \
    CalculateMostExpensiveCountryUseCase
from src.features.statistics.domain.use_cases.calculate_price_change_use_case import CalculatePriceChangeUseCase
from src.features.statistics.domain.use_cases.get_extremities_per_country_use_case import \
    GetExtremitiesPerCountryUseCase


class BigMacApplication:

    @staticmethod
    async def run() -> None:
        csv_file_path: pathlib.Path = constants.PROJECT_ROOT.absolute().joinpath(
            pathlib.Path('input/big_mac_prices.csv')
        )
        csv_file_reader: CsvFileReader = CsvFileReader()
        csv_price_mapper: CsvPriceMapper = CsvPriceMapper()

        csv_data_source: CsvDataSource = CsvDataSource(
            csv_file_path=csv_file_path,
            csv_file_reader=csv_file_reader,
        )

        price_repository: PriceRepository = PriceRepositoryImpl(
            csv_data_source=csv_data_source,
            csv_price_model_mapper=csv_price_mapper,
        )

        load_prices_use_case: LoadPricesUseCase = LoadPricesUseCase(
            price_repository=price_repository,
        )
        calculate_average_price_per_country_use_case: CalculateAveragePricePerCountryUseCase = \
            CalculateAveragePricePerCountryUseCase()
        most_expensive_country_use_case: CalculateMostExpensiveCountryUseCase = CalculateMostExpensiveCountryUseCase()
        cheapest_country_use_case: CalculateCheapestCountryUseCase = CalculateCheapestCountryUseCase()
        get_extremities_use_case: GetExtremitiesPerCountryUseCase = GetExtremitiesPerCountryUseCase()
        calculate_price_change_use_case: CalculatePriceChangeUseCase = CalculatePriceChangeUseCase()

        main_menu_controller: MainMenuController = MainMenuController(
            load_prices_use_case=load_prices_use_case,
            calculate_average_price_per_country_use_case=calculate_average_price_per_country_use_case,
            calculate_most_expensive_country_use_case=most_expensive_country_use_case,
            calculate_cheapest_country_use_case=cheapest_country_use_case,
            get_extremities_per_country_use_case=get_extremities_use_case,
            calculate_price_change_use_case=calculate_price_change_use_case,
        )

        main_menu: MainMenu = MainMenu(
            main_menu_controller=main_menu_controller,
        )

        while True:
            await main_menu.run()
