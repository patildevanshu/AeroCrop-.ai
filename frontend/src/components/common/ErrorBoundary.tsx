import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[ErrorBoundary caught error]:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div
          className="card glass"
          style={{
            padding: '1.5rem',
            margin: '1rem 0',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            background: 'rgba(239, 68, 68, 0.08)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '1.4rem' }}>⚠️</span>
            <h3 style={{ margin: 0, color: '#f87171', fontSize: '1rem' }}>
              {this.props.fallbackTitle || 'Component Error (घटक त्रुटी)'}
            </h3>
          </div>
          <p style={{ margin: '0 0 0.8rem 0', fontSize: '0.84rem', color: '#cbd5e1' }}>
            A temporary display error occurred while rendering this section. Your data is safe.
          </p>
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => this.setState({ hasError: false })}
          >
            🔄 Try Again (पुन्हा प्रयत्न करा)
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
