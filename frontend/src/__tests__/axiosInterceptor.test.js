import axios from 'axios';
import { registerAxiosInterceptor } from '../services/axiosInterceptor';
import { toast } from 'react-toastify';

jest.mock('axios', () => ({
  interceptors: {
    response: {
      use: jest.fn(),
    },
  },
}));

jest.mock('react-toastify', () => ({
  toast: {
    error: jest.fn(),
  },
}));

describe('axios interceptor', () => {
  it('displays toast on failed request', async () => {
    registerAxiosInterceptor();

    // Capture the error handler registered with axios
    const errorHandler = axios.interceptors.response.use.mock.calls[0][1];

    const error = { response: { data: { detail: 'Request failed' } } };

    // Invoke the interceptor's error handler
    await expect(errorHandler(error)).rejects.toBe(error);

    expect(toast.error).toHaveBeenCalledWith('Request failed');
  });
});
