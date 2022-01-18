/* eslint-disable no-unused-vars */
import {xu} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil} from "xutil";
import {path, delay} from "std";

const testData = xu.parseJSON(await Deno.readTextFile(path.join("/mnt/dexvert/test", `${Deno.hostname()}.json`)));
const formats = {};
for(const o of Object.values(testData))
{
	if(!o.processed || o.family!=="archive")
		continue;
	
	if(!Object.hasOwn(formats, o.format))
		formats[o.format] = {allSingle : true};
	
	if(!formats[o.format]?.allSingle)
		continue;
	
	if(Object.values(o.files).length!==1)
		formats[o.format].allSingle = false;
}

for(const [formatid, {allSingle}] of Object.entries(formats))
{
	if(!allSingle)
		continue;
	
	console.log(formatid);
}
