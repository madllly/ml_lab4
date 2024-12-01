import argparse
import itertools
import json

import joblib
import pandas as pd
import wandb
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def train_and_log(config, dataset_path, experiment_name):
    if not isinstance(config, dict):
        raise TypeError(f"Invalid config type: {type(config)}. Expected dict.")

    # Генерация всех возможных комбинаций параметров
    param_combinations = list(itertools.product(*config.values()))

    # Загрузка данных
    data = pd.read_csv(dataset_path)
    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Для каждой комбинации параметров обучаем модель
    for params in param_combinations:
        model_config = dict(zip(config.keys(), params))
        print(f"Training with config: {model_config}")

        # Инициализация W&B с уникальным именем для каждого эксперимента
        experiment_name_unique = f"{experiment_name}_{'_'.join(map(str, params))}"
        wandb.init(project="ml_experiments", config=model_config, name=experiment_name_unique)

        model = RandomForestRegressor(
            **model_config
        )  # Используем регрессор с конкретной комбинацией параметров
        model.fit(X_train, y_train)

        # Предсказания и метрики
        predictions = model.predict(X_test)

        # В случае регрессии метрики могут быть R^2, MSE, MAE
        mae = mean_absolute_error(y_test, predictions)
        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)

        # Логирование метрик в W&B
        wandb.log({"MAE": mae, "MSE": mse, "R2": r2})

        # Сохранение модели в корневую директорию
        model_path = f"output/{experiment_name_unique}_model_{str(params)}.pkl"
        try:
            joblib.dump(model, model_path)
            print(f"Model saved to {model_path}")
        except Exception as e:
            print(f"Failed to save model: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Path to config JSON")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset path")
    parser.add_argument("--experiment", type=str, required=True, help="Experiment name")
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    train_and_log(config, args.dataset, args.experiment)
