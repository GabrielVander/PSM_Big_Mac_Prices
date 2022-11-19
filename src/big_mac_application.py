import pathlib

import constants
from src.core.data.data_sources.csv_data_source import CsvDataSource
from src.core.data.data_sources.utils.csv_file_reader import CsvFileReader
from src.core.data.repositories.mappers.csv_price_mapper import CsvPriceMapper
from src.core.data.repositories.price_repository_impl import PriceRepositoryImpl
from src.core.domain.repository.price_repository import PriceRepository
from src.core.domain.use_cases.load_prices_use_case import LoadPricesUseCase
from src.core.presentation.main_menu import MainMenu
from src.features.price_provisioning.price_provisioning_controller import PriceProvisioningController
from src.features.statistics.domain.use_cases.calculate_average_price_per_country_use_case import \
    CalculateAveragePricePerCountryUseCase
from src.features.statistics.statistics_controller import StatisticsController


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
            csv_file_reader=csv_file_reader
        )

        price_repository: PriceRepository = PriceRepositoryImpl(
            csv_data_source=csv_data_source,
            csv_price_model_mapper=csv_price_mapper
        )

        load_prices_use_case: LoadPricesUseCase = LoadPricesUseCase(
            price_repository=price_repository
        )
        calculate_average_price_per_country_use_case = CalculateAveragePricePerCountryUseCase()

        price_provisioning_controller: PriceProvisioningController = PriceProvisioningController(
            load_prices_use_case=load_prices_use_case
        )
        statistics_controller: StatisticsController = StatisticsController(
            load_prices_use_case=load_prices_use_case,
            average_price_use_case=calculate_average_price_per_country_use_case
        )

        main_menu: MainMenu = MainMenu(
            price_provisioning_controller=price_provisioning_controller,
            statistics_controller=statistics_controller
        )

        while True:
            await main_menu.run()
