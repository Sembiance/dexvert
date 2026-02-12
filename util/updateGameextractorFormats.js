import {xu} from "xu";
import {C} from "../src/C.js";
import {XLog} from "xlog";
import {path} from "std";
import {printUtil, fileUtil} from "xutil";
import {_SKIP_CODES, _SKIP_NAMES} from "../src/program/detect/gameextractorID.js";

const xlog = new XLog();

const list = [];
for(const {name, code, games, extensions} of await xu.fetch(`http://${C.GAMEEXTRACTOR_HOST}:${C.GAMEEXTRACTOR_PORT}/list`, {asJSON : true}))
{
	if(_SKIP_CODES.some(v => code.startsWith(v)) || _SKIP_NAMES.some(v => name.startsWith(v)))
		continue;

	const o = {};
	o.code = code;
	o.name = "";
	if(code!==name)
		o.name = name;

	o.extensions = extensions.join(", ");
	o.games = games.join(", ");

	list.push(o);
}

const table = printUtil.columnizeObjects(list.sortMulti([o => o.code]), {
	alignment :
	{
		code       : "r",
		name       : "l",
		extensions : "l"
	}
}).decolor();

await fileUtil.searchReplace(path.join(import.meta.dirname, "..", "sandbox", "txt", "programs_formats.txt"), />>> gameextractor.*<<< gameextractor/s, `>>> gameextractor (run dra util/updateGameextractorFormats.js to update)\n${table}\n<<< gameextractor`);
