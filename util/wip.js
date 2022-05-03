/* eslint-disable no-unused-vars */
import {xu} from "xu";
import {XLog} from "xlog";
import {runUtil, fileUtil, printUtil} from "xutil";
import {path, delay, base64Encode} from "std";
import {formats, reload as reloadFormats} from "../src/format/formats.js";

const xlog = new XLog();

const formatValues = Object.values(formats).filter(f => f.familyid==="image");

const recoilFormats = [];
const noMatchingFormats = [];
const noRecoilFormats = [];

const tomsExts = [".256", ".ap2", ".ch4", ".ch6", ".chs", ".64c", ".ch8", ".psd", ".ocp", ".afl", ".rla", ".grf", ".ami", ".acbm", ".lbm", ".iff", ".ilbm", ".atk", ".a4r", ".app", ".pict", ".vollabel", ".pnt", ".art", ".art", ".aas", ".a64", ".4mi", ".4pl", ".art", ".agp", ".all", ".pzm", ".dgp", ".dgi", ".esc", ".apv", ".ilc", ".ap3", ".apc", ".plm", ".cpr", ".doo", ".drg", ".fnt", ".g10", ".gfb", ".gr7", ".gr8", ".gr9", ".hr", ".inp", ".mch", ".mgp", ".mis", ".pic", ".pla", ".apl", ".shc", ".4pm", ".acs", ".atr", ".hlr", ".sld", ".cel", ".kro", ".epa", ".inlin", ".ybm", ".eyuv", ".bpg", ".bg9", ".g09", ".bfli", ".pic", ".rad", ".biorad", ".pi", ".chr", ".wnd", ".bob", ".pix", ".bgp", ".raw", ".crw", ".cr2", ".cpt", ".cdu", ".cci", ".cin", ".che", ".cip", ".clp", ".cmuwm", ".cbr", ".cbz", ".csv", ".fiasco", ".gif", ".cis", ".cals", ".ca2", ".ca3", ".ca1", ".cwg", ".nlq", ".pc3", ".pc1", ".pc2", ".bl2", ".bl3", ".bl1", ".bru", ".pi1", ".pi3", ".pi2", ".dph", ".del", ".dcm", ".ddbug", ".dng", ".din", ".dlm", ".dds", ".djvu", ".qrt", ".dis", ".dol", ".dd", ".brush", ".jj", ".dhr", ".cut", ".drl", ".dlp", ".drz", ".drp", ".duo", ".du1", ".du2", ".aai", ".dgu", ".dg1", ".dgc", ".dc1", ".eci", ".ecp", ".trp", ".epdf", ".esm", ".escp2", ".ximg", ".fpt", ".ftc", ".ffli", ".fits", ".fts", ".fd2", ".fli", ".bml", ".fmv", ".pi4", ".pi9", ".raf", ".fgs", ".fwa", ".fun", ".fp2", ".gd2", ".gd", ".img", ".ghg", ".gcd", ".gig", ".gih", ".gbr", ".h", ".xcf", ".pat", ".4bt", ".god", ".gould", ".sr8", ".dot", ".g11", ".spc", ".hpm", ".grf", ".p41", ".pix", ".g3", ".fax", ".ifl", ".gun", ".hip", ".hr2", ".hci", ".hed", ".hpc", ".exr", ".hgr", ".hgb", ".hips", ".hrs", ".hfc", ".hlf", ".him", ".hbm", ".hir", ".ham6", ".ham8", ".hdiff", ".pj", ".thinkjet", ".htm", ".html", ".kps", ".icn", ".imn", ".ipc", ".ip2", ".info", ".ish", ".ism", ".tru", ".ing", ".iim", ".int", ".ice", ".ige", ".ihe", ".ist", ".leaf", ".uyvy", ".iph", ".ipt", ".ipi", ".ithmb", ".jbig", ".jgp", ".jpe", ".jpg", ".jfi", ".jif", ".jfif", ".jpeg", ".jp2k", ".jxr", ".j2c", ".jpt", ".j2k", ".jp2", ".viff", ".koa", ".kla", ".gg", ".dcr", ".kpr", ".leo", ".bbg", ".rfg", ".lispm", ".lp3", ".sys", ".ldm", ".mac", ".macp", ".mbg", ".rys", ".cpi", ".mat", ".mcs", ".mgr", ".mil", ".mda", ".avi", ".cur", ".ico", ".msp", ".bmp", ".dib", ".mlt", ".bb0", ".bb1", ".bb2", ".bb4", ".scs4", ".bb5", ".mono", ".mon", ".bkg", ".mic", ".shp", ".mrf", ".mtv", ".ozb", ".ozt", ".mpp", ".mle", ".mg1", ".mg2", ".mg4", ".mg8", ".mc", ".mng", ".neo", ".nsr", ".nef", ".ngf", ".ngg", ".nlm", ".nol", ".npm", ".565", ".orf", ".otb", ".p11", ".p4i", ".pk", ".pmg", ".pdb", ".pdbim", ".palm", ".mcpp", ".pcl", ".pef", ".picon", ".art", ".pgx", ".pcds", ".pcd", ".pcs", ".p64", ".pl4", ".pmd", ".2bp", ".pnm", ".rppm", ".pgm", ".rpgm", ".pbm", ".ppm", ".rpbm", ".pam", ".pdf", ".pfm", ".apng", ".png", ".pgf", ".pgc", ".pgx", ".bum", ".psid", ".pfa", ".pfb", ".psb", ".mbm", ".pzl", ".cm", ".ptif", ".hdr", ".rp", ".rm4", ".rm0", ".rm3", ".rm1", ".rm2", ".raw", ".txt", ".rip", ".rpm", ".sar", ".sbig", ".svg", ".ipl", ".sct", ".scr", ".sca", ".yjk", ".srs", ".scc", ".grp", ".sc2", ".ge5", ".sc5", ".sc7", ".ge7", ".sc8", ".sfw", ".pwp", ".sge", ".shr", ".x3f", ".bw", ".sgi", ".rgb", ".rgba", ".p", ".hrz", ".dpx", ".sir", ".mrw", ".arw", ".411", ".spu", ".sps", ".spot", ".spr", ".srf", ".ps1", ".pac", ".avs", ".x", ".icon", ".rast", ".sun", ".sunicon", ".irg", ".ir2", ".sif", ".sxs", ".tip", ".tga", ".targa", ".lum", ".73i", ".82i", ".83i", ".8xi", ".85i", ".86i", ".92i", ".9xi", ".v2i", ".tiff", ".tim", ".tn4", ".tn3", ".tn1", ".tn2", ".tny", ".mci", ".mcp", ".txs", ".fs", ".rle", ".ptx", ".bm", ".vbm", ".vzi", ".vic", ".vicar", ".vid", ".ska", ".rap", ".vst", ".wrl", ".webp", ".wbz", ".wig", ".wzl", ".wbmp", ".wpg", ".xwd", ".xpm", ".xbm", ".xga", ".xim", ".xlp", ".max", ".xvmini", ".p7", ".yuv", ".zeiss", ".dcx", ".3", ".zxp"];	// eslint-disable-line max-len
for(const tomsExt of tomsExts)
{
	const matchingFormats = formatValues.filter(f => (f?.ext || []).includes(tomsExt));
	if(matchingFormats.length===0)
	{
		noMatchingFormats.push(tomsExt);
		continue;
	}

	const allConverters = matchingFormats.flatMap(matchingFormat => (matchingFormat.converters && Array.isArray(matchingFormat.converters) ? matchingFormat.converters : []));
	const hasRecoil = allConverters.some(converter => typeof converter==="string" && (converter.startsWith("recoil2png") || converter.startsWith("darktable_cli")));
	if(hasRecoil)
		recoilFormats.push(`${tomsExt} : ${matchingFormats.map(f => f.formatid).join(", ")}`);
	else
		noRecoilFormats.push(`${tomsExt} : ${matchingFormats.map(f => f.formatid).join(", ")}`);
}

console.log(printUtil.majorHeader("Recoil Formats Found"));
console.log(recoilFormats.join("\n"));

console.log(printUtil.majorHeader("No Recoil Formats Found"));
console.log(noRecoilFormats.join("\n"));

console.log(printUtil.majorHeader("No Formats Found"));
console.log(noMatchingFormats.join("\n"));


/*const raw = await Deno.readFile("/tmp/desktop.ini");
const textDecoder = new TextDecoder();
const text = textDecoder.decode(raw);
console.log(base64Encode(text));
*/

