"""
Student Assignment Management Module
Provides utilities for managing personalized assignments and dataset details.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any


# Assignment Configuration Database
ASSIGNMENT_DATABASE = {
    'r1111111': {
        'dataset': 'iris.csv',
        'required_features': ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
        'TARGET': 'species',
        'task_type': 'classification',
        'difficulty': 'beginner'
    },
    'r2222222': {
        'dataset': 'house_prices.csv',
        'required_features': ['square_feet', 'bedrooms', 'bathrooms', 'age', 'location_score'],
        'TARGET': 'price',
        'task_type': 'regression',
        'difficulty': 'intermediate'
    },
    'r3333333': {
        'dataset': 'customer_churn.csv',
        'required_features': ['age', 'tenure', 'monthly_charges', 'total_charges', 'contract_type'],
        'TARGET': 'churn',
        'task_type': 'classification',
        'difficulty': 'intermediate'
    },
    'r4444444': {
        'dataset': 'student_performance.csv',
        'required_features': ['study_hours', 'attendance', 'previous_gpa', 'assignments_completed'],
        'TARGET': 'final_grade',
        'task_type': 'regression',
        'difficulty': 'beginner'
    },
    'r5555555': {
        'dataset': 'credit_card_fraud.csv',
        'required_features': ['amount', 'merchant_category', 'transaction_hour', 'days_since_last_transaction', 'mcc'],
        'TARGET': 'is_fraud',
        'task_type': 'classification',
        'difficulty': 'advanced'
    },
}


def generate_assignment(student_id: str) -> Dict[str, Any]:
    """
    Generate a personalized assignment for a student.
    
    Parameters:
    -----------
    student_id : str
        The student's ID (e.g., 'r1111111')
    
    Returns:
    --------
    dict : Assignment details including dataset, features, and target
    
    Raises:
    -------
    ValueError : If student_id is not found in the database
    """
    if student_id not in ASSIGNMENT_DATABASE:
        # Return default assignment for unknown IDs
        return {
            'dataset': 'iris.csv',
            'required_features': ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'],
            'TARGET': 'species',
            'task_type': 'classification',
            'difficulty': 'beginner'
        }
    
    return ASSIGNMENT_DATABASE[student_id].copy()


def print_assignment_details(student_id: str) -> Dict[str, Any]:
    """
    Print and return detailed assignment information for a student.
    
    Parameters:
    -----------
    student_id : str
        The student's ID
    
    Returns:
    --------
    dict : Assignment parameters
    """
    assignment = generate_assignment(student_id)
    
    print("=" * 80)
    print("PERSONALIZED ASSIGNMENT DETAILS")
    print("=" * 80)
    print(f"\nStudent ID: {student_id}")
    print(f"Dataset: {assignment['dataset']}")
    print(f"Task Type: {assignment['task_type'].upper()}")
    print(f"Difficulty Level: {assignment['difficulty'].upper()}")
    print(f"\nTarget Variable: {assignment['TARGET']}")
    print(f"\nRequired Features ({len(assignment['required_features'])} total):")
    for i, feature in enumerate(assignment['required_features'], 1):
        print(f"  {i}. {feature}")
    print("\n" + "=" * 80 + "\n")
    
    return assignment


def validate_features(df: pd.DataFrame, required_features: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that all required features exist in the dataframe.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The dataset
    required_features : list
        List of required feature names
    
    Returns:
    --------
    tuple : (is_valid, missing_features)
    """
    missing = [f for f in required_features if f not in df.columns]
    return len(missing) == 0, missing


def get_task_metrics(task_type: str) -> Dict[str, List[str]]:
    """
    Get appropriate evaluation metrics based on task type.
    
    Parameters:
    -----------
    task_type : str
        Either 'classification' or 'regression'
    
    Returns:
    --------
    dict : Dictionary with primary and secondary metrics
    """
    if task_type.lower() == 'classification':
        return {
            'primary': ['accuracy', 'f1_score', 'precision', 'recall'],
            'secondary': ['roc_auc', 'confusion_matrix', 'classification_report'],
            'cv_metric': 'f1_weighted'
        }
    elif task_type.lower() == 'regression':
        return {
            'primary': ['mse', 'rmse', 'mae', 'r2_score'],
            'secondary': ['residuals', 'actual_vs_predicted'],
            'cv_metric': 'r2'
        }
    else:
        raise ValueError(f"Unknown task type: {task_type}")


def suggest_models(task_type: str, difficulty: str = 'beginner') -> Dict[str, List[str]]:
    """
    Suggest appropriate models based on task type and difficulty.
    
    Parameters:
    -----------
    task_type : str
        Either 'classification' or 'regression'
    difficulty : str
        'beginner', 'intermediate', or 'advanced'
    
    Returns:
    --------
    dict : Suggested models grouped by complexity
    """
    suggestions = {
        'classification': {
            'beginner': ['LogisticRegression', 'DecisionTreeClassifier'],
            'intermediate': ['RandomForestClassifier', 'GradientBoostingClassifier', 'SVC'],
            'advanced': ['XGBClassifier', 'LGBMClassifier', 'VotingClassifier', 'StackingClassifier']
        },
        'regression': {
            'beginner': ['LinearRegression', 'Ridge', 'Lasso'],
            'intermediate': ['RandomForestRegressor', 'GradientBoostingRegressor', 'SVR'],
            'advanced': ['XGBRegressor', 'LGBMRegressor', 'VotingRegressor', 'StackingRegressor']
        }
    }
    
    if task_type not in suggestions:
        raise ValueError(f"Unknown task type: {task_type}")
    
    return suggestions[task_type]


def create_experiment_log() -> pd.DataFrame:
    """
    Create an empty experiment log dataframe for tracking model performance.
    
    Returns:
    --------
    pd.DataFrame : Empty dataframe with experiment tracking columns
    """
    return pd.DataFrame(columns=[
        'experiment_id',
        'model_name',
        'hyperparameters',
        'cv_score_mean',
        'cv_score_std',
        'test_score',
        'training_time_seconds',
        'notes'
    ])


def log_experiment(log: pd.DataFrame, experiment_id: int, model_name: str,
                   hyperparams: Dict, cv_mean: float, cv_std: float,
                   test_score: float, train_time: float, notes: str = '') -> pd.DataFrame:
    """
    Add an experiment record to the experiment log.
    
    Parameters:
    -----------
    log : pd.DataFrame
        Experiment log dataframe
    experiment_id : int
        Experiment number
    model_name : str
        Name of the model
    hyperparams : dict
        Hyperparameters used
    cv_mean : float
        Cross-validation mean score
    cv_std : float
        Cross-validation std score
    test_score : float
        Test set score
    train_time : float
        Training time in seconds
    notes : str
        Optional notes about the experiment
    
    Returns:
    --------
    pd.DataFrame : Updated log
    """
    new_row = pd.DataFrame([{
        'experiment_id': experiment_id,
        'model_name': model_name,
        'hyperparameters': str(hyperparams),
        'cv_score_mean': round(cv_mean, 4),
        'cv_score_std': round(cv_std, 4),
        'test_score': round(test_score, 4),
        'training_time_seconds': round(train_time, 2),
        'notes': notes
    }])
    
    return pd.concat([log, new_row], ignore_index=True)


def display_experiment_summary(log: pd.DataFrame) -> None:
    """
    Display a formatted summary of all experiments.
    
    Parameters:
    -----------
    log : pd.DataFrame
        Experiment log dataframe
    """
    if log.empty:
        print("No experiments logged yet.")
        return
    
    print("\n" + "=" * 100)
    print("EXPERIMENT SUMMARY")
    print("=" * 100)
    print(log.to_string(index=False))
    print("=" * 100 + "\n")
    
    best_idx = log['test_score'].idxmax()
    best_model = log.loc[best_idx]
    print(f"Best Performing Model: {best_model['model_name']}")
    print(f"Test Score: {best_model['test_score']:.4f}")
    print(f"Hyperparameters: {best_model['hyperparameters']}\n")


# Utility functions for data exploration

def analyze_class_distribution(y: pd.Series) -> Dict[str, Any]:
    """
    Analyze class distribution for classification tasks.
    
    Parameters:
    -----------
    y : pd.Series
        Target variable
    
    Returns:
    --------
    dict : Distribution statistics
    """
    value_counts = y.value_counts()
    
    return {
        'classes': value_counts.index.tolist(),
        'counts': value_counts.values.tolist(),
        'proportions': (value_counts / len(y)).round(4).to_dict(),
        'is_balanced': (value_counts.max() / value_counts.min()) < 1.5,
        'imbalance_ratio': value_counts.max() / value_counts.min()
    }


def identify_outliers_iqr(data: pd.DataFrame, features: List[str]) -> Dict[str, int]:
    """
    Identify outliers using IQR method.
    
    Parameters:
    -----------
    data : pd.DataFrame
        The dataset
    features : list
        Numeric features to check
    
    Returns:
    --------
    dict : Number of outliers per feature
    """
    outliers = {}
    
    for col in features:
        if data[col].dtype in ['int64', 'float64']:
            Q1 = data[col].quantile(0.25)
            Q3 = data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            outliers[col] = ((data[col] < lower) | (data[col] > upper)).sum()
    
    return outliers


if __name__ == '__main__':
    # Example usage
    print_assignment_details('r1111111')
    print_assignment_details('r2222222')
