import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {C} from "../../C.js";

// these codes are known to match lots of random files based on current dexvert test samples, so just exclude them entirely from appearing
const _SKIP_CODES = new Set([
	"AFS_AFS_WE00", "AMM_FORM", "ARC_ARC", "ARK_2", "CEG_GEKV", "BIN_6", "BIN_7L", "BMP_BMP", "DAT_57", "DAT_CMP_2", "DBS", "DLL_MZ",
	"FBZ_PK", "FFMPEG_Audio_", "FLA", "GUT", "ISO", "JavaImagingUtilities", "LBM_FORM", "MHTML", "MP3",
	"NoExt_1", "NoExt_2", "NoExt_3", "NoExt_4", "NoExt_6", "NoExt_7", "NoExt_8", "NoExt_RDFZ",
	"PAK_11", "PAK_42", "PAK_43", "PAK_55", "PAK_FORM", "PAK_G3V0", "PCG", "PCK_2", "PKBARC_BMT", "PKF", "PRJ_PROJ",
	"SHD", "SND_SND2", "TEXTURE", "TXT", "U_Generic", "VGMSTREAM_Audio_WAV_RIFF", "WAD_8", "WAV_RIFF", "ZBD_RIFF", "ZIP_PK"
]);
const _SKIP_NAMES = ["Unity3D Engine Resource"];
export {_SKIP_CODES, _SKIP_NAMES};

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
			if((!r.xlog || !r.xlog.atLeast("trace")) && (_SKIP_CODES.has(code) || _SKIP_NAMES.some(v => name.startsWith(v))))
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
				r.meta.detections.push(Detection.create({value : vals.join(""), from : "gameextractorID", extensions : (extensions || []).sortMulti().map(v => `.${v}`), confidence, weak : confidence<=15, file : r.f.input}));
			}
		}
	};
	renameOut = false;
}
