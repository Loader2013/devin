import { appendUserMessage } from "../state/chatSlice";
import Socket from "../socket/socket";
import store from "../store";

export function sendChatMessage(message: string): void {
  store.dispatch(appendUserMessage(message));
  const event = { action: "start", args: { task: message } };
  const eventString = JSON.stringify(event);
  Socket.send(eventString);
}
