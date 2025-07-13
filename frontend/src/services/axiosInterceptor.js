import axios from 'axios';
import { toast } from 'react-toastify';

export function registerAxiosInterceptor() {
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      const message =
        error?.response?.data?.detail || error.message || 'Request failed';
      toast.error(message);
      return Promise.reject(error);
    },
  );
}
