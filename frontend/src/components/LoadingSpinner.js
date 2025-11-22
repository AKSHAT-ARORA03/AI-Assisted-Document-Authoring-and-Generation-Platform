import React from 'react';

const LoadingSpinner = ({ size = 'medium', className = '' }) => {
  const sizeClasses = {
    small: 'h-4 w-4 border',
    medium: 'h-8 w-8 border-2',
    large: 'h-12 w-12 border-2'
  };

  return (
    <div 
      className={`animate-spin rounded-full ${sizeClasses[size]} border-primary-600 border-t-transparent ${className}`}
    />
  );
};

export default LoadingSpinner;