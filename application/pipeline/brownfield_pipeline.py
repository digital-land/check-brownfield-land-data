import functools

from digital_land.convert import Converter
from digital_land.normalise import Normaliser
from digital_land.map import Mapper
from digital_land.harmonise import Harmoniser

from digital_land.pipeline import Pipeline
from digital_land.specification import Specification
from digital_land.issues import Issues, IssuesFile
from digital_land.organisation import Organisation
from digital_land.load import LineConverter
from digital_land.plugin import get_plugin_manager
from digital_land.collection import Collection
from digital_land.save import save


def compose(*functions):
    def compose2(f, g):
        return lambda x: g(f(x))

    return functools.reduce(compose2, functions, lambda x: x)


class CollectionlessHarmoniser(Harmoniser):
    def set_resource_defaults(self, resource):
        if not resource:
            return

        self.default_fieldnames = self.pipeline.default_fieldnames(resource=None)
        if self.plugin_manager:
            self.plugin_manager.hook.set_resource_defaults_post(resource=None)


class BrownfieldPipeline:
    def init(self):
        self.pipeline = Pipeline("pipeline/", "brownfield-land")
        self.specification = Specification("specification/")
        self.plugin_manager = get_plugin_manager()

        schema = self.specification.pipeline[self.pipeline.name]["schema"]
        fieldnames = self.specification.schema_field[schema].copy()
        replacement_fields = list(self.pipeline.transformations().keys())
        for field in replacement_fields:
            if field in fieldnames:
                fieldnames.remove(field)

        self.intermediary_fieldnames = fieldnames

    def process(self, resource_file_path, harmonised_file_path, issues_file_path):
        resource_hash = ""
        issues = Issues()
        patch = self.pipeline.patches(resource_hash)

        collection = Collection()
        line_converter = LineConverter()
        converter = Converter(self.pipeline.conversions())

        normaliser = Normaliser(self.pipeline.skip_patterns(resource_hash))
        mapper = Mapper(
            self.intermediary_fieldnames,
            self.pipeline.columns(resource_hash),
            self.pipeline.concatenations(resource_hash),
        )
        harmoniser = CollectionlessHarmoniser(
            self.specification,
            self.pipeline,
            issues,
            collection,
            Organisation().organisation_uri,
            patch,
            self.plugin_manager,
        )

        pipeline = compose(
            converter.convert,
            normaliser.normalise,
            line_converter.convert,
            mapper.map,
            harmoniser.harmonise,
        )

        output = pipeline(resource_file_path)
        save(output, harmonised_file_path, fieldnames=self.intermediary_fieldnames)
        issues_file = IssuesFile(path=issues_file_path)
        issues_file.write_issues(issues)


pipeline = BrownfieldPipeline()
