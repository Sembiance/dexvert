import {Program} from "../../Program.js";

const KEY_VAL_HEADERS = ["fileheader", "dosimage"];
const ARRAY_HEADERS = ["optionalheader32bit", "datadirectory"];
const NUMS =
[
	"bytesOnLastPage", "numberOfPages", "relocations", "sizeOfHeader", "minExtraParagraphs", "maxExtraParagraphs", "overlayNumber", "relocationFile",	// EXE
	"autoDataSegment", "numberOfSegments", "numberOfModrefs"	// DLL
];
const HEX_NUMS = ["offsetToExtHeader"];
const ARRAY_SUBCATS = ["characteristics"];

export const _WINDUMP_META_KEYS = [...KEY_VAL_HEADERS, ...ARRAY_HEADERS];

export class winedump extends Program
{
	website = "https://www.winehq.org/";
	package = "app-forensics/winedump";
	bin     = "winedump";
	args    = r => ["dump", r.inFile()];
	post    = r =>
	{
		const meta = {};
		let category = null;
		let subcat = null;

		r.stdout.trim().split("\n").forEach(line =>
		{
			const lineCat = line.trimChars(" :").strip(" ()").toLowerCase();
			if(_WINDUMP_META_KEYS.includes(lineCat))
			{
				category = lineCat;
				subcat = null;
			}
			else if(category)
			{
				const props = (line.match(/^\s*(?<key>[^:]+):\s+(?<val>.+)\s*$/) || {})?.groups;
				const propValue = props ? props.val : line.trim();
				const propKey = props ? props.key.trim().strip("()-").toCamelCase() : null;

				if(propValue.length===0)
				{
					category = null;
					return;
				}

				if(KEY_VAL_HEADERS.includes(category))
				{
					meta[category] ||= {};

					if(subcat)
					{
						if(ARRAY_SUBCATS.includes(subcat))
							meta[category][subcat].push(propValue);
						else
							meta[category][subcat] = NUMS.includes(propKey) ? +propValue : (HEX_NUMS.includes(propKey) ? parseInt(propValue, 16) : propValue);
					}
					else if(ARRAY_SUBCATS.includes(propKey))
					{
						subcat = propKey;
						meta[category][subcat] = [];
					}
					else if(propKey)
					{
						meta[category][propKey] = NUMS.includes(propKey) ? +propValue : (HEX_NUMS.includes(propKey) ? parseInt(propValue, 16) : propValue);
					}
				}
				else
				{
					meta[category] ||= [];
					meta[category].push(propValue);
				}
			}
		});

		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
