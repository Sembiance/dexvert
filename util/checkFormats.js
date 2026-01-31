import {xu} from "xu";
import {XLog} from "xlog";
import {initRegistry} from "../src/dexUtil.js";
import {formats} from "../src/format/formats.js";

const xlog = new XLog("info");
await initRegistry(xlog);

for(const [formatid, format] of Object.entries(formats))
{
	for(const ext of format.ext || [])
	{
		if(["mapBrowserVectorData"].includes(formatid))
			continue;

		if(["_", "$"].includes(ext))
			continue;

		if(!ext.startsWith("."))
			xlog.info`format ${formatid} has an ext that does not start with a period: ${ext}`;
	}
}
