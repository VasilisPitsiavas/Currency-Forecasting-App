# Cryptocurrency Forecasting App

## Overview

The **Cryptocurrency Forecasting App** predicts cryptocurrency prices using machine learning models. Specifically, the project utilizes **ARIMAX** (AutoRegressive Integrated Moving Average with Exogenous Variables) for time-series forecasting. This app fetches both real-time and historical cryptocurrency price data and performs predictions based on factors such as market volume, high and low prices, and other market metrics.

By leveraging historical market data and external variables, the app aims to provide accurate predictions for cryptocurrency prices, which can assist traders in decision-making.

## Features

- **Real-Time Data Fetching**: Automatically fetches current cryptocurrency price data through an API.
- **Historical Data Loading**: Loads and processes historical price data to train the forecasting model.
- **ARIMAX Model**: Forecasts the price using the ARIMAX model, considering external features such as volume and price history.
- **XGBoost Model**: Forecasts the price using the XGBoost algorithm with additional functionalities like grid search for hyperparameter tuning and lag feature creation.
- **Hyperparameter Tuning**: Performs grid search to optimize model hyperparameters and find the best configuration.
- **Data Visualization**:  The app visualizes the predictions, allowing users to easily compare model outputs with actual data.

## Prerequisites

Before getting started, make sure you have the following installed on your system:

- Python 3.9 or higher
- Pip (Python package installer)
- An API key for fetching cryptocurrency data

## Installation

### 1. Clone the Repository

First, clone the repository to your local machine using the following command:

```bash
git clone https://github.com/yourusername/cryptocurrency-forecasting-app.git