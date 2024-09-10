import { SERVER_URL } from "../constants";
const URL = `${SERVER_URL}/robot/control`;

const sendCommand = async (command: string): Promise<any> => {
  const response = await fetch(`${URL}/${command}`, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(`Error fetching items: ${response.statusText}`);
  }
  const data = await response.json();
  return data;
};

export default {
  sendCommand,
};
