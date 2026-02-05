import {xu} from "xu";
import {path} from "std";
import {hostUtil} from "/mnt/compendium/DevLab/xpriv/xpriv.js";

const DEXDRONE_TRUTH_HOST = "dexdrone0";
export {DEXDRONE_TRUTH_HOST};

const isDexdrone = hostUtil.HOSTS[Deno.hostname()].roles.includes("dexdrone");
export function mkWeblink(diskPath)
{
	return `file://${isDexdrone ? `/mnt/dexvert/dexdrone/${Deno.hostname()}/${(diskPath ? path.relative("/mnt/dexvert", diskPath) : diskPath).encodeURLPath()}` : diskPath.encodeURLPath()}`;
}
