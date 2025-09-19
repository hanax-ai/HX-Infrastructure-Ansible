#!/usr/bin/env python3
"""
Comprehensive AI/ML Model Training Suite
Trains all AI models for the HX Infrastructure platform
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import yaml
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveModelTrainer:
    def __init__(self, config_path='/opt/hx/ai-ml/config.yml'):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        self.models = {}
        self.scalers = {}
        
    def _load_config(self, config_path):
        """Load configuration"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return self._default_config()
    
    def _default_config(self):
        """Default configuration"""
        return {
            'models_path': '/opt/hx/ai-models',
            'data_path': '/opt/hx/training-data',
            'log_path': '/var/log/hx-ai-training',
            'training_params': {
                'test_size': 0.2,
                'random_state': 42,
                'cv_folds': 5
            }
        }
    
    def _setup_logging(self):
        """Setup logging"""
        os.makedirs('/var/log/hx-ai-training', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/hx-ai-training/model_training.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def generate_synthetic_data(self):
        """Generate synthetic training data for all models"""
        self.logger.info("Generating synthetic training data...")
        
        # Deployment decision data
        deployment_data = self._generate_deployment_data()
        
        # Anomaly detection data
        anomaly_data = self._generate_anomaly_data()
        
        # Performance prediction data
        performance_data = self._generate_performance_data()
        
        # Cost optimization data
        cost_data = self._generate_cost_data()
        
        # Multi-cloud placement data
        placement_data = self._generate_placement_data()
        
        return {
            'deployment': deployment_data,
            'anomaly': anomaly_data,
            'performance': performance_data,
            'cost': cost_data,
            'placement': placement_data
        }
    
    def _generate_deployment_data(self):
        """Generate deployment decision training data"""
        data = []
        for i in range(5000):
            cpu = np.random.normal(60, 20)
            memory = np.random.normal(70, 15)
            error_rate = np.random.exponential(0.5)
            traffic = np.random.lognormal(5, 1)
            hour = np.random.randint(0, 24)
            day = np.random.randint(0, 7)
            maintenance = 1 if 2 <= hour <= 4 else 0
            recent_deploys = np.random.poisson(2)
            
            # Rule-based strategy selection
            if error_rate > 1.0 or cpu > 90:
                strategy = 0  # blue_green
            elif traffic > 1000 and not maintenance:
                strategy = 1  # canary
            elif maintenance:
                strategy = 2  # rolling
            else:
                strategy = np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2])
            
            data.append([cpu, memory, error_rate, traffic, hour, day, maintenance, recent_deploys, strategy])
        
        return pd.DataFrame(data, columns=[
            'cpu_utilization', 'memory_utilization', 'error_rate', 'traffic_load',
            'hour_of_day', 'day_of_week', 'is_maintenance_window', 'recent_deployments', 'strategy'
        ])
    
    def _generate_anomaly_data(self):
        """Generate anomaly detection training data"""
        # Normal data
        normal_data = []
        for i in range(8000):
            cpu = np.random.normal(50, 15)
            memory = np.random.normal(60, 12)
            disk_io = np.random.normal(100, 30)
            network_io = np.random.normal(50, 20)
            response_time = np.random.normal(200, 50)
            error_rate = np.random.exponential(0.1)
            
            normal_data.append([cpu, memory, disk_io, network_io, response_time, error_rate, 0])
        
        # Anomalous data
        anomaly_data = []
        for i in range(2000):
            # Create various types of anomalies
            anomaly_type = np.random.choice(['cpu_spike', 'memory_leak', 'disk_issue', 'network_issue'])
            
            if anomaly_type == 'cpu_spike':
                cpu = np.random.normal(95, 5)
                memory = np.random.normal(60, 12)
                disk_io = np.random.normal(100, 30)
                network_io = np.random.normal(50, 20)
                response_time = np.random.normal(500, 100)
                error_rate = np.random.exponential(0.5)
            elif anomaly_type == 'memory_leak':
                cpu = np.random.normal(50, 15)
                memory = np.random.normal(95, 5)
                disk_io = np.random.normal(100, 30)
                network_io = np.random.normal(50, 20)
                response_time = np.random.normal(400, 80)
                error_rate = np.random.exponential(0.3)
            elif anomaly_type == 'disk_issue':
                cpu = np.random.normal(50, 15)
                memory = np.random.normal(60, 12)
                disk_io = np.random.normal(500, 100)
                network_io = np.random.normal(50, 20)
                response_time = np.random.normal(800, 150)
                error_rate = np.random.exponential(0.2)
            else:  # network_issue
                cpu = np.random.normal(50, 15)
                memory = np.random.normal(60, 12)
                disk_io = np.random.normal(100, 30)
                network_io = np.random.normal(200, 50)
                response_time = np.random.normal(1000, 200)
                error_rate = np.random.exponential(0.4)
            
            anomaly_data.append([cpu, memory, disk_io, network_io, response_time, error_rate, 1])
        
        all_data = normal_data + anomaly_data
        return pd.DataFrame(all_data, columns=[
            'cpu_utilization', 'memory_utilization', 'disk_io', 'network_io',
            'response_time', 'error_rate', 'is_anomaly'
        ])
    
    def _generate_performance_data(self):
        """Generate performance prediction training data"""
        data = []
        for i in range(10000):
            # System metrics
            cpu = np.random.normal(60, 20)
            memory = np.random.normal(70, 15)
            disk_io = np.random.normal(100, 30)
            network_io = np.random.normal(50, 20)
            
            # Load characteristics
            concurrent_users = np.random.poisson(100)
            request_rate = np.random.poisson(1000)
            
            # Time features
            hour = np.random.randint(0, 24)
            day = np.random.randint(0, 7)
            
            # Calculate response time based on system state
            base_response_time = 100
            cpu_impact = max(0, (cpu - 70) * 5)
            memory_impact = max(0, (memory - 80) * 3)
            load_impact = (concurrent_users / 10) + (request_rate / 100)
            
            response_time = base_response_time + cpu_impact + memory_impact + load_impact
            response_time += np.random.normal(0, 20)  # Add noise
            
            data.append([cpu, memory, disk_io, network_io, concurrent_users, 
                        request_rate, hour, day, response_time])
        
        return pd.DataFrame(data, columns=[
            'cpu_utilization', 'memory_utilization', 'disk_io', 'network_io',
            'concurrent_users', 'request_rate', 'hour_of_day', 'day_of_week', 'response_time'
        ])
    
    def _generate_cost_data(self):
        """Generate cost optimization training data"""
        data = []
        for i in range(5000):
            # Resource configuration
            cpu_cores = np.random.choice([2, 4, 8, 16, 32])
            memory_gb = np.random.choice([4, 8, 16, 32, 64])
            storage_gb = np.random.choice([100, 500, 1000, 2000])
            
            # Utilization
            cpu_util = np.random.normal(60, 20)
            memory_util = np.random.normal(70, 15)
            storage_util = np.random.normal(50, 20)
            
            # Cloud provider and region
            provider = np.random.choice([0, 1, 2])  # AWS, Azure, GCP
            region = np.random.choice([0, 1, 2, 3, 4])
            
            # Instance type
            instance_type = np.random.choice([0, 1, 2, 3])  # general, compute, memory, storage optimized
            
            # Calculate cost based on configuration
            base_cost = cpu_cores * 0.05 + memory_gb * 0.01 + storage_gb * 0.0001
            provider_multiplier = [1.0, 0.95, 0.9][provider]  # AWS, Azure, GCP
            region_multiplier = np.random.uniform(0.8, 1.2)
            
            hourly_cost = base_cost * provider_multiplier * region_multiplier
            
            data.append([cpu_cores, memory_gb, storage_gb, cpu_util, memory_util, 
                        storage_util, provider, region, instance_type, hourly_cost])
        
        return pd.DataFrame(data, columns=[
            'cpu_cores', 'memory_gb', 'storage_gb', 'cpu_utilization', 
            'memory_utilization', 'storage_utilization', 'provider', 'region',
            'instance_type', 'hourly_cost'
        ])
    
    def _generate_placement_data(self):
        """Generate multi-cloud placement training data"""
        data = []
        for i in range(3000):
            # Workload characteristics
            workload_type = np.random.choice([0, 1, 2, 3])  # web, database, compute, storage
            cpu_requirement = np.random.choice([1, 2, 4, 8, 16])
            memory_requirement = np.random.choice([2, 4, 8, 16, 32])
            storage_requirement = np.random.choice([10, 50, 100, 500, 1000])
            
            # Performance requirements
            latency_requirement = np.random.choice([10, 50, 100, 500])  # ms
            availability_requirement = np.random.choice([99.0, 99.9, 99.95, 99.99])
            
            # Geographic requirements
            region_preference = np.random.choice([0, 1, 2, 3, 4])  # US-East, US-West, EU, Asia, Global
            
            # Compliance requirements
            data_residency = np.random.choice([0, 1])
            encryption_required = np.random.choice([0, 1])
            
            # Cost sensitivity
            cost_priority = np.random.uniform(0, 1)
            
            # Optimal cloud selection (rule-based for training)
            if workload_type == 1 and availability_requirement > 99.9:  # Database, high availability
                optimal_cloud = 0  # AWS
            elif workload_type == 2 and cpu_requirement > 8:  # Compute intensive
                optimal_cloud = 2  # GCP
            elif cost_priority > 0.7:  # Cost sensitive
                optimal_cloud = 2  # GCP (typically cheaper)
            elif data_residency and region_preference == 2:  # EU compliance
                optimal_cloud = 1  # Azure (good EU presence)
            else:
                optimal_cloud = np.random.choice([0, 1, 2])
            
            data.append([workload_type, cpu_requirement, memory_requirement, storage_requirement,
                        latency_requirement, availability_requirement, region_preference,
                        data_residency, encryption_required, cost_priority, optimal_cloud])
        
        return pd.DataFrame(data, columns=[
            'workload_type', 'cpu_requirement', 'memory_requirement', 'storage_requirement',
            'latency_requirement', 'availability_requirement', 'region_preference',
            'data_residency', 'encryption_required', 'cost_priority', 'optimal_cloud'
        ])
    
    def train_deployment_model(self, data):
        """Train deployment decision model"""
        self.logger.info("Training deployment decision model...")
        
        X = data.drop('strategy', axis=1)
        y = data['strategy']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config['training_params']['test_size'],
            random_state=self.config['training_params']['random_state']
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        
        self.logger.info(f"Deployment model - Train: {train_score:.3f}, Test: {test_score:.3f}, CV: {cv_scores.mean():.3f}")
        
        self.models['deployment'] = model
        self.scalers['deployment'] = scaler
        
        return model, scaler
    
    def train_anomaly_model(self, data):
        """Train anomaly detection model"""
        self.logger.info("Training anomaly detection model...")
        
        X = data.drop('is_anomaly', axis=1)
        y = data['is_anomaly']
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train Isolation Forest
        model = IsolationForest(contamination=0.2, random_state=42)
        model.fit(X_scaled[y == 0])  # Train only on normal data
        
        # Evaluate
        predictions = model.predict(X_scaled)
        predictions = (predictions == -1).astype(int)  # Convert to binary
        accuracy = accuracy_score(y, predictions)
        
        self.logger.info(f"Anomaly model accuracy: {accuracy:.3f}")
        
        self.models['anomaly'] = model
        self.scalers['anomaly'] = scaler
        
        return model, scaler
    
    def train_performance_model(self, data):
        """Train performance prediction model"""
        self.logger.info("Training performance prediction model...")
        
        X = data.drop('response_time', axis=1)
        y = data['response_time']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config['training_params']['test_size'],
            random_state=self.config['training_params']['random_state']
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        y_pred = model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        
        self.logger.info(f"Performance model - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}, MSE: {mse:.2f}")
        
        self.models['performance'] = model
        self.scalers['performance'] = scaler
        
        return model, scaler
    
    def train_cost_model(self, data):
        """Train cost prediction model"""
        self.logger.info("Training cost prediction model...")
        
        X = data.drop('hourly_cost', axis=1)
        y = data['hourly_cost']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config['training_params']['test_size'],
            random_state=self.config['training_params']['random_state']
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        
        self.logger.info(f"Cost model - Train R²: {train_score:.3f}, Test R²: {test_score:.3f}")
        
        self.models['cost'] = model
        self.scalers['cost'] = scaler
        
        return model, scaler
    
    def train_placement_model(self, data):
        """Train multi-cloud placement model"""
        self.logger.info("Training placement model...")
        
        X = data.drop('optimal_cloud', axis=1)
        y = data['optimal_cloud']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.config['training_params']['test_size'],
            random_state=self.config['training_params']['random_state']
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = model.score(X_train_scaled, y_train)
        test_score = model.score(X_test_scaled, y_test)
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        
        self.logger.info(f"Placement model - Train: {train_score:.3f}, Test: {test_score:.3f}, CV: {cv_scores.mean():.3f}")
        
        self.models['placement'] = model
        self.scalers['placement'] = scaler
        
        return model, scaler
    
    def save_models(self):
        """Save all trained models"""
        models_path = self.config['models_path']
        os.makedirs(models_path, exist_ok=True)
        
        for model_name, model in self.models.items():
            model_file = os.path.join(models_path, f"{model_name}_model.pkl")
            scaler_file = os.path.join(models_path, f"{model_name}_scaler.pkl")
            
            with open(model_file, 'wb') as f:
                pickle.dump(model, f)
            
            with open(scaler_file, 'wb') as f:
                pickle.dump(self.scalers[model_name], f)
            
            self.logger.info(f"Saved {model_name} model to {model_file}")
        
        # Save metadata
        metadata = {
            'training_date': datetime.now().isoformat(),
            'models_trained': list(self.models.keys()),
            'config': self.config
        }
        
        with open(os.path.join(models_path, 'training_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def train_all_models(self):
        """Train all AI/ML models"""
        try:
            self.logger.info("Starting comprehensive model training...")
            
            # Generate training data
            training_data = self.generate_synthetic_data()
            
            # Train all models
            self.train_deployment_model(training_data['deployment'])
            self.train_anomaly_model(training_data['anomaly'])
            self.train_performance_model(training_data['performance'])
            self.train_cost_model(training_data['cost'])
            self.train_placement_model(training_data['placement'])
            
            # Save models
            self.save_models()
            
            self.logger.info("All models trained successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Model training failed: {e}")
            return False

if __name__ == '__main__':
    trainer = ComprehensiveModelTrainer()
    success = trainer.train_all_models()
    sys.exit(0 if success else 1)
