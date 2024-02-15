import {xu} from "xu";
import {runUtil} from "xutil";
import {runTerminal, runTerminalCommand} from "awesomewm";
//import {C} from "../src/C.js";
import {hostUtil} from "/mnt/compendium/DevLab/xpriv/xpriv.js";
import {path} from "std";

const DEXDRONE_DIR_PATH = "/mnt/dexvert/dexdrone";

const dexdroneHosts = Object.entries(hostUtil.HOSTS).filter(([, hostInfo]) => hostInfo.roles.includes("dexdrone")).map(([hostid]) => hostid);
const {wid} = await runTerminal("", {tabName : Deno.hostname()});
while(dexdroneHosts.length)
{
	const dexdroneHost = dexdroneHosts.shift();
	const dexdroneDirPath = path.join(DEXDRONE_DIR_PATH, dexdroneHost);
	await Deno.mkdir(dexdroneDirPath, {recursive : true});
	await runUtil.run("sshfs", [`${dexdroneHost}:/mnt/dexvert`, dexdroneDirPath]);
	await runTerminalCommand(wid, `ssh sembiance@${dexdroneHost}\ncd /mnt/compendium/DevLab/dexvert\nreset\n`, {newTab : true, tabName : dexdroneHost});
}
