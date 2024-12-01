#!/bin/bash -x

# Загружаем переменные из .env
set -o allexport
source .env
set +o allexport

CONFIG_PATH=$1
EXPERIMENT_NAME=$2

if [ -z "$CONFIG_PATH" ] || [ -z "$EXPERIMENT_NAME" ]; then
  echo "Usage: $0 <config_path> <experiment_name>"
  exit 1
fi

# Проверяем существование файла конфигурации
if [ ! -f "$CONFIG_PATH" ]; then
  echo "Error: Config file $CONFIG_PATH does not exist."
  exit 1
fi

# Проверяем, что переменные окружения заданы
if [ -z "$MINIO_ENDPOINT" ] || [ -z "$MINIO_ROOT_USER" ] || [ -z "$MINIO_ROOT_PASSWORD" ]; then
  echo "Error: S3 environment variables are not set."
  exit 1
fi

# Генерируем все возможные комбинации параметров
param_combinations=$(python -c "
import json
import itertools
with open('$CONFIG_PATH') as f:
    config = json.load(f)
    param_combinations = list(itertools.product(*config.values()))
    for params in param_combinations:
        print('$EXPERIMENT_NAME_' + '_'.join(map(str, params)))
")

# Для каждой комбинации параметров запускаем отдельный эксперимент
for experiment_name_unique in $param_combinations; do
  echo "Running experiment: $experiment_name_unique"

  docker run --rm \
    --network my_network \
    --env WANDB_API_KEY=$WANDB_API_KEY \
    -v "$(pwd)/lab3:/app/lab3" \
    -v "$(pwd)/output:/app/output" \
    trainer:latest \
    python lab3/scripts/train_model.py \
    --config "/app/$CONFIG_PATH" \
    --dataset "/app/lab3/titanic_processed.csv" \
    --experiment "$experiment_name_unique"
done




