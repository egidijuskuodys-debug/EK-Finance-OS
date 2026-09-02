from importers.base_importer import BaseImporter
from importers.ibkr_importer import IBKRImporter
from importers.revolut_importer import RevolutImporter
from importers.seb_importer import SEBImporter


class ImporterFactory:
    _importers = {
        "IBKR": IBKRImporter,
        "INTERACTIVE_BROKERS": IBKRImporter,
        "SEB": SEBImporter,
        "REVOLUT": RevolutImporter,
    }

    @classmethod
    def get_importer(
        cls,
        broker: str,
        file_path: str,
    ) -> BaseImporter:
        normalized_broker = (
            broker.strip()
            .upper()
            .replace(" ", "_")
        )

        importer_class = cls._importers.get(
            normalized_broker
        )

        if importer_class is None:
            supported_brokers = ", ".join(
                sorted(cls._importers.keys())
            )

            raise ValueError(
                f"Unsupported broker: '{broker}'. "
                f"Supported brokers: {supported_brokers}."
            )

        return importer_class(file_path)