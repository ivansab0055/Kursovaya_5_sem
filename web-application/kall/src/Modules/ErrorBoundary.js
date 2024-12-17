import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = {hasError: false};
    }

    static getDerivedStateFromError(error) {
        return {hasError: true};
    }

    componentDidCatch(error, errorInfo) {
        if (process.env.REACT_APP_NODE_ENV === 'development')
            console.error("Error caught in ErrorBoundary:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return null; // Замените на то, что хотите показать вместо ошибки
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
