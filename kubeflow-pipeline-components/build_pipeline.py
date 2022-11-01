import kfp
from kfp import dsl, compiler


PIPELINE_NAME = "Kubeflow Pipeline Components Tutorial"
DESCRIPTION = "Pipeline to learn how to construct pipeline"

download_csv_data_spec = "components_spec/download_csv_data.yaml"
split_csv_data_spec = "components_spec/split_csv_data.yaml"
norm_data_spec = "components_spec/normalize_data.yaml"
train_model_spec = "components_spec/train_model.yaml"
eval_model_spec = "components_spec/eval_model.yaml"


@dsl.pipeline(
    name=PIPELINE_NAME,
    description=DESCRIPTION
)
def execute(data_url: str,
            test_size: float,
            batch_size: int,
            epochs: int,
            learning_rate: float
            ):
    # load yaml
    download_csv_data = kfp.components.load_component_from_file(download_csv_data_spec)
    split_csv_data = kfp.components.load_component_from_file(split_csv_data_spec)
    norm_data = kfp.components.load_component_from_file(norm_data_spec)
    train_model = kfp.components.load_component_from_file(train_model_spec)
    eval_model = kfp.components.load_component_from_file(eval_model_spec)

    # define task
    download_csv_data_task = download_csv_data(data_url=data_url)
    split_csv_data_task = split_csv_data(
        input_csv=download_csv_data_task.outputs['output_csv'],
        test_size=test_size
    )
    norm_data_task = norm_data(
        train_csv=split_csv_data_task.outputs["train_csv"],
        test_csv=split_csv_data_task.outputs["test_csv"],
    )
    train_model_task = train_model(
        train_features=norm_data_task.outputs["train_features"],
        train_labels=norm_data_task.outputs["train_labels"],
        learning_rate=learning_rate,
        epochs=epochs,
        batch_size=batch_size
    )
    eval_model_task = eval_model(
        test_features=norm_data_task.outputs["test_features"],
        test_labels=norm_data_task.outputs["test_labels"],
        model_path=train_model_task.outputs["model_path"]
    )
    return


if __name__ == '__main__':
    compiler.Compiler().compile(execute, 'pipeline.yaml')