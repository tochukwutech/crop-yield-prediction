# Climate-Based Multi-Crop Yield Prediction in Nigeria

## Project Overview
This project focuses on developing a machine learning approach for estimating the yields of selected crops in Nigeria using historical agricultural and climate data.

It aims to investigate the relationship between climatic conditions, particularly rainfall and temperature, and crop yields. By combining historical agricultural records with relevant climate data, the project will explore regression-based machine learning models to estimate crop yields and evaluate their performance.

The project will cover multiple selected crops in Nigeria, with the final crop selection depending on the availability and quality of historical data.

## Problem Statement
Agricultural production is influenced by several environmental factors, including rainfall and temperature. Variations in these climatic conditions can affect crop growth and ultimately influence agricultural yields.

In Nigeria, understanding the relationship between climate conditions and crop yields is important for analysing agricultural productivity and supporting informed decision-making. However, estimating crop yields across different crops and locations requires relevant historical agricultural and climate data to be collected, prepared and analysed.

This project seeks to address this by integrating historical agricultural and climate datasets and applying machine learning regression techniques to estimate the yields of selected crops in Nigeria based on climatic conditions observed throughout their growing seasons.


## Project Aim and Objectives
The project intends to:

1. Obtain relevant historical agricultural and climate data for selected crops in Nigeria.
2. Examine how climate factors, such as rainfall and temperature, relate to crop yields.
3. Prepare and integrate the collected datasets for machine learning.
4. Explore suitable regression algorithms for estimating crop yields.
5. Compare the performance of the selected models to determine which provides the most reliable estimates.

## Proposed Methodology
The project proposes using supervised machine learning to estimate the yields of multiple crops in Nigeria. Historical crop yield records will be combined with climate data to examine how environmental conditions throughout the growing season relate to agricultural productivity. The model will use factors such as crop type, geographical location, rainfall, and temperatures as input variables, while the recorded crop yield will serve as the target variable.
We intend to explore regression algorithms such as Linear Regression, Random Forest Regression, and Gradient Boosting. Their performance will be compared to determine which approach provides the most reliable crop yield estimates.


## Dataset and Data Sources
The project will use historical agricultural and climate datasets relevant to selected crops and locations in Nigeria.

The proposed data sources include:

1. **GROW-Africa Database:** A source of historical agricultural data, including crop yield observations across African countries.
   - https://zenodo.org/records/16544448

2. **HarvestStat Africa:** A harmonised agricultural database containing crop production, harvested area and yield statistics across African countries.
   - https://datadryad.org/dataset/doi:10.5061/dryad.vq83bk42w

3. **CHIRPS:** A climate data source providing historical rainfall estimates.
   - https://www.chc.ucsb.edu/data/chirps

4. **NASA POWER:** A source of meteorological data, including temperature and other climate variables.
   - https://power.larc.nasa.gov/data-access-viewer/

The agricultural datasets will provide crop yield information, while the climate datasets will provide relevant environmental variables such as rainfall and temperature.

The collected datasets will be assessed, cleaned and integrated based on crop, geographical location and relevant growing season to prepare them for exploratory data analysis and machine learning.

The final selection of datasets and crops will depend on data availability, coverage, consistency and suitability for the project.

## Technologies and Libraries
For this machine learning project, we made use of:
- Python (Technology)
- Pandas (Library)
- NumPy (Library)
- Scikit-Learn (Library)
- Matplotlib (Library)
- Seaborn (Library)

## Project Structure

```text
crop-yield-prediction/
│
├── data/
│   ├── raw/ - Original agricultural and climate datasets
│   └── processed/ - Cleaned and prepared datasets
│
├── notebooks/ - Jupyter notebooks for data exploration and experiments
│
├── src/ - Python scripts for data preprocessing and model development
│
├── models/ - Saved machine learning models
│
├── results/ - Model evaluation results, charts and visualisations
│
├── report/ - Project documentation and final report
│
├── README.md - Project overview and documentation
│
├── requirements.txt - Python project dependencies
│
└── .gitignore - Files and directories excluded from Git
```

## Team Members
- David Offor (Project Lead)
- Fahd Animashaun
- Faisal Farouk-Muazu
- Muhammed-Faiz Oyebanji

## Project Status
**Current Stage:** Initial Setup

The project is currently in its initial setup phase. The team is establishing the development environment, organising the GitHub repository and preparing to collect and explore the required agricultural and climate datasets.

Upcoming activities include:
- Agricultural and climate data collection.
- Data cleaning and preprocessing.
- Exploratory data analysis.
- Machine learning model development.
- Model evaluation and comparison.