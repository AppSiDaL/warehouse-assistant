import { SERVER_URL } from "../constants";
const URL = `${SERVER_URL}/items`;

const getItems = async (): Promise<any> => {
  const response = await fetch(`${URL}`);
  if (!response.ok) {
    throw new Error(`Error fetching items: ${response.statusText}`);
  }
  const data = await response.json();
  return data;
};

const createItem = async (id: string): Promise<any> => {
  const data = {
    user: id,
  };
  const response = await fetch(URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Error creating item: ${response.statusText}`);
  }
  const responseData = await response.json();
  return responseData;
};

export default {
  getItems,
  createItem,
};