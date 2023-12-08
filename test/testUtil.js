import {xu} from "xu";
import {path} from "std";
import {hostUtil} from "xpriv";

const isDexdrone = hostUtil.HOSTS[Deno.hostname()].roles.includes("dexdrone");
export function mkWeblink(diskPath)
{
	return `file://${isDexdrone ? `/mnt/dexvert/dexdrone/${Deno.hostname()}/${diskPath ? path.relative("/mnt/dexvert", diskPath) : diskPath}` : diskPath}`;
}
