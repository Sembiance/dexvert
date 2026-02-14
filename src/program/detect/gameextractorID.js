import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {C} from "../../C.js";

// these codes are known to match lots of random files based on current dexvert test samples, so just exclude them entirely from appearing
const _WEAK_PREFIX_CODES =
{
	35 : ["NoExt_"],
	30 : ["BIN_", "DAT_", "NoExt_", "PAK_"],
	25 : ["RES_", "WAD_"]
};
const _SKIP_CODES = new Set([
	"AFS_AFS_WE00", "AMM_FORM", "ARC_ARC", "ARK_2", "CEG_GEKV", "BMP_BMP", "DBS", "DLL_MZ",
	"FBZ_PK", "FLA", "GUT", "ISO", "JavaImagingUtilities", "LBM_FORM", "MHTML", "MP3",
	"PAK_FORM", "PCG", "PCK_2", "PKBARC_BMT", "PKF", "PRJ_PROJ",
	"SHD", "SND_SND2", "TEXTURE", "TXT", "U_Generic", "WAV_RIFF", "ZBD_RIFF", "ZIP_PK"
]);
const _SKIP_PREFIX_CODES = [];
const _SKIP_PREFIX_NAMES = ["Unity3D Engine Resource"];
export {_SKIP_CODES, _SKIP_PREFIX_CODES, _SKIP_PREFIX_NAMES};

export class gameextractorID extends Program
{
	website = "https://sourceforge.net/projects/gameextractor/files/";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		const result = await xu.fetch(`http://${C.GAMEEXTRACTOR_HOST}:${C.GAMEEXTRACTOR_PORT}/detect`, {json : {filePath : r.inFile({absolute : true})}, asJSON : true});
		for(const {type, code, name, rating, extensions, games, extensionMatch} of result?.matches || [])
		{
			if((!r.xlog || !r.xlog.atLeast("trace")) && (_SKIP_CODES.has(code) || _SKIP_PREFIX_CODES.some(v => code.startsWith(v)) || _SKIP_PREFIX_NAMES.some(v => name.startsWith(v))))
				continue;

			const confidence = Math.clamp(rating - (extensionMatch ? 25 : 0), 0, 100);
			if(confidence>0)
			{
				const vals = [];
				vals.push(`ge${type}: `);
				vals.push(code);
				if(name!==code)
					vals.push(` - ${name}`);
				if((games || []).length && games.some(v => v?.length))
					vals.push(` (${games.sortMulti().slice(0, 2).join(", ")}${games.length>3 ? `, ${games.length-3} more...` : ""})`);
				const weak = confidence<=(r.f.input.size<100 ? 49 : 15) || (Object.entries(_WEAK_PREFIX_CODES).some(([lowCon, codes]) => codes.some(v => code.startsWith(v)) && confidence<=lowCon));
				r.meta.detections.push(Detection.create({value : vals.join(""), from : "gameextractorID", extensions : (extensions || []).sortMulti().map(v => `.${v}`), confidence, weak, file : r.f.input}));
			}
		}
	};
	renameOut = false;
}
