import {xu} from "xu";
import {fileUtil} from "xutil";
import {path} from "std";

const formatCounts = {};
(await fileUtil.tree(path.join(import.meta.dirname, "sample"), {nodir : true, relative : true})).forEach(filePath =>
{
	const [family, format] = filePath.split("/");
	const formatid = `${family}/${format}`;
	formatCounts[formatid] ||= 0;
	formatCounts[formatid]++;
});

console.log(JSON.stringify(formatCounts));
