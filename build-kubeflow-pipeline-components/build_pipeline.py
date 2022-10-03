import kfp
from kfp import dsl, compiler


PIPELINE_NAME = "Kubeflow Pipeline Components Tutorial"
DESCRIPTION = "Pipeline to learn how to construct pipeline"

download_csv_data_spec = "components_spec/download_csv_data.yaml"
split_csv_data_spec = "components_spec/split_csv_data.yaml"
norm_data_spec = "components_spec/normalize_data.yaml"


@dsl.pipeline(
    name=PIPELINE_NAME,
    description=DESCRIPTION
)
def execute(url: str,
            test_size: float
            ):
    # load yaml
    download_csv_data = kfp.components.load_component_from_file(download_csv_data_spec)
    split_csv_data = kfp.components.load_component_from_file(split_csv_data_spec)
    norm_data = kfp.components.load_component_from_file(norm_data_spec)

    # define task
    download_csv_data_task = download_csv_data(url=url)
    split_csv_data_task = split_csv_data(
        input_csv=download_csv_data_task.outputs['output_csv'],
        test_size=test_size
    )
    norm_data_task = norm_data(
        train_csv=split_csv_data_task.outputs["train_csv"],
        test_csv=split_csv_data_task.outputs["test_csv"],
    )
    return


if __name__ == '__main__':
    compiler.Compiler().compile(execute, 'pipeline.yaml')