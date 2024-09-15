import RobotService from "../services/robot";
// Find all buttons with the `alert` class on the page.
const buttons = document.querySelectorAll("button.alert");

// Handle clicks on each button.
buttons.forEach((button) => {
  button.addEventListener("click", () => {
    const command = button.getAttribute("data-command");
    handleCommandSend(command ?? "");
  });
});

const handleCommandSend = (command: string) => {
  RobotService.sendCommand(command);
};
