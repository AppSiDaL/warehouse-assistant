import { ROBOT_URL,SERVER_URL } from "../constants";
const URL = `${ROBOT_URL}/control`;

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

const fetchMap = async () => {
  const response = await fetch(`${SERVER_URL}/robot/get_map_image`);
  if (!response.ok) {
    throw new Error(`Error fetching items: ${response.statusText}`);
  }
  const blob = await response.blob();

  return blob;
};

const fetchRobotPosition =async () =>{
  const response = await fetch(`${SERVER_URL}/robot/get_location`);
  if (!response.ok) {
    throw new Error("Failed to fetch robot position");
  }
  return response;
}

export default {
  sendCommand,
  fetchRobotPosition,
  fetchMap,
};
