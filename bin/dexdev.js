import {xu} from "xu";
import {runUtil} from "xutil";
import {switchToWorkspace, setLayout, runTerminal, runTerminalCommand} from "awesomewm";

const runOptions = {inheritEnv : true};
await switchToWorkspace(1, 2);
await runTerminal("dexserver\n");
await runTerminal("retrodev\n");

await switchToWorkspace(2, 2);
await setLayout("browserVerticalDev", 2, 2);
const {wid : ccWID} = await runTerminal();
await runUtil.run("mybrave", ["--new-window", "http://overseer.retromission.com"], {detached : true, ...runOptions});	// can't associate to a browser window, so we just run manually here
await runTerminalCommand(ccWID, "ssh sembiance@chatsubo\nreset\n");
await runTerminalCommand(ccWID, "ssh sembiance@chatsubo\nreset\n", {newTab : true});
await runTerminalCommand(ccWID, "ssh sembiance@pax\nreset\n", {newTab : true});
await runTerminalCommand(ccWID, "", {newTab : true});

await switchToWorkspace(4, 2);
const {wid : devBottomWID} = await runTerminal();
const {wid : devTopWID} = await runTerminal();
await runTerminalCommand(devTopWID, "cd Assorted\nreset\n");
await runTerminalCommand(devTopWID, "cd Assorted\nreset\n", {newTab : true});

await runTerminalCommand(devBottomWID, "cd /mnt/compendium/DevLab/dexvert/test/sample\nreset\n", {cmdDelay : 400});
await runTerminalCommand(devBottomWID, "cd /mnt/compendium/DevLab/dexvert/sandbox/triddefs/defs\nreset\n", {newTab : true});
await runTerminalCommand(devBottomWID, "cd /usr/share/misc/magic\nreset\n", {newTab : true});
await runTerminalCommand(devBottomWID, "cd /mnt/compendium/DevLab/dexvert/test\n", {newTab : true});
