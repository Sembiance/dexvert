import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

const DEXMAGIC_CHECKS =
{
	"CAD/Draw TVG"             : "TommySoftware TVG",
	"Second Nature Slide Show" : "Second Nature Software\r\nSlide Show\r\nCollection"
};
Object.mapInPlace(DEXMAGIC_CHECKS, (k, v) => (typeof v==="string" ? ([k, [{offset : 0, match : v}]]) : v));
Object.values(DEXMAGIC_CHECKS).flat().forEach(check =>
{
	if(typeof check.match==="string")
		check.match = (new TextEncoder()).encode(check.match);
});
const DEXMAGIC_BYTES_MAX = Object.values(DEXMAGIC_CHECKS).flat().map(check => (check.offset+check.match.length)).max();

export class dexmagic extends Program
{
	website = "https://github.com/Sembiance/dexvert/tree/master/src/program/detect/dexmagic.js";
	loc = "local";

	exec = async r =>
	{
		r.meta.detections = [];

		const f = await Deno.open(r.input.primary.absolute);
		const buf = new Uint8Array(DEXMAGIC_BYTES_MAX);
		await Deno.read(f.rid, buf); // 11 bytes
		Deno.close(f.rid);
		
		for(const [matchid, checks] of Object.entries(DEXMAGIC_CHECKS))
		{
			let match=true;
			for(const check of checks)
			{
				for(let loc=check.offset, i=0;i<check.match.length;loc++, i++)
				{
					if(buf[loc]!==check.match[i])
					{
						match = false;
						break;
					}
				}

				if(!match)
					break;
			}

			if(!match)
				continue;
			
			r.meta.detections.push(Detection.create({value : matchid, from : "dexmagic", file : r.inputOriginal.primary}));
		}
	}
}
