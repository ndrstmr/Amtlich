import axios from 'axios';

const API_URL = `${process.env.REACT_APP_API_URL}/api`;

export const registerUserIfNeeded = async (firebaseUser) => {
  if (!firebaseUser) return;

  await axios.post(`${API_URL}/auth/register`, {
    firebase_uid: firebaseUser.uid,
    email: firebaseUser.email,
    name: firebaseUser.displayName || firebaseUser.email,
    role: 'viewer',
  });
};

export const fetchUserFromServer = async () => {
  const response = await axios.get(`${API_URL}/auth/me`);
  return response.data;
};
