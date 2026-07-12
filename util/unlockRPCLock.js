import {xu} from "xu";
import {C} from "../src/C.js";
import {cmdUtil} from "xutil";
import {XLog} from "xlog";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	desc : "Will forcefully unlock a given lock",
	args :
	[
		{argid : "lockid", desc : "Which lockid to unlock", required : true}
	]});

await xu.waitUntil(async () => (await (await fetch(`http://${C.DEXRPC_HOST}:${C.DEXRPC_PORT}/unlock`, {method : "POST", headers : { "content-type" : "application/json" }, body : JSON.stringify({lockid : argv.lockid})}))?.text())==="true");

xlog.info`Unlocked lockid: ${argv.lockid}`;
