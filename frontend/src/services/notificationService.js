import { toast } from 'react-toastify';

// Custom toast configurations with Matrix theme
const toastConfig = {
  position: "top-right",
  autoClose: 4000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  style: {
    background: 'rgba(0, 20, 0, 0.95)',
    border: '1px solid #00ff88',
    color: '#00ff88',
    fontFamily: 'monospace',
    backdropFilter: 'blur(10px)'
  }
};

export const notify = {
  success: (message, options = {}) => {
    toast.success(message, {
      ...toastConfig,
      ...options,
      className: 'matrix-toast-success',
      progressClassName: 'matrix-toast-progress-success',
    });
  },

  error: (message, options = {}) => {
    toast.error(message, {
      ...toastConfig,
      ...options,
      className: 'matrix-toast-error',
      progressClassName: 'matrix-toast-progress-error',
      style: {
        ...toastConfig.style,
        border: '1px solid #ff0044',
        color: '#ff0044',
      }
    });
  },

  info: (message, options = {}) => {
    toast.info(message, {
      ...toastConfig,
      ...options,
      className: 'matrix-toast-info',
      progressClassName: 'matrix-toast-progress-info',
      style: {
        ...toastConfig.style,
        border: '1px solid #00ccff',
        color: '#00ccff',
      }
    });
  },

  warning: (message, options = {}) => {
    toast.warning(message, {
      ...toastConfig,
      ...options,
      className: 'matrix-toast-warning',
      progressClassName: 'matrix-toast-progress-warning',
      style: {
        ...toastConfig.style,
        border: '1px solid #ffaa00',
        color: '#ffaa00',
      }
    });
  },

  loading: (message, options = {}) => {
    return toast.loading(message, {
      ...toastConfig,
      ...options,
      autoClose: false,
      className: 'matrix-toast-loading',
    });
  },

  promise: (promise, messages) => {
    return toast.promise(
      promise,
      {
        pending: {
          render() {
            return messages.pending || 'Processing...';
          },
          ...toastConfig
        },
        success: {
          render({ data }) {
            return messages.success || 'Success!';
          },
          ...toastConfig
        },
        error: {
          render({ data }) {
            return messages.error || 'Error occurred';
          },
          ...toastConfig,
          style: {
            ...toastConfig.style,
            border: '1px solid #ff0044',
            color: '#ff0044',
          }
        }
      }
    );
  }
};

export default notify;
