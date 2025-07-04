import {xu} from "xu";
import {Format} from "../../Format.js";

export class jpg extends Format
{
	name             = "Joint Photographic Experts Group Image";
	website          = "http://fileformats.archiveteam.org/wiki/JPEG";
	ext              = [".jpg", ".jpeg", ".jpe", ".jfif"];
	mimeType         = "image/jpeg";
	magic            = [
		"JFIF JPEG bitmap", "JPEG image data", "JPEG bitmap", "JPEG File Interchange Format", "JFIF-EXIF JPEG Bitmap", "Macintosh JPEG bitmap (MacBinary)", "HSI JPEG bitmap", "image/jpeg", "piped jpeg sequence (jpeg_pipe)",
		"JPEG Stereoscopic bitmap", "deark: jpeg (JPEG/Exif)", "deark: jpeg (JPEG/JFIF", "deark: jpeg (JPEG (other))", /^deark: jpeg$/, /^JPEG (CMYK|Grayscale|TrueColor) \(v[\d.]+\) :(frm|fsy|jpeg|jps):$/, "JPEG based file :*:",
		"Pegasus JPEG bitmap",	// supposedly a variant of JPEG but it seems to work just fine as a normal JPEG
		/^fmt\/(41|42|43|44|645|1507)( |$)/, /^x-fmt\/(390|391|398)( |$)/];
	idMeta           = ({macFileType}) => ["JFIF", "JPEG", "jpeg"].includes(macFileType);
	fallback         = true;	// Some other formats such as image/a4r can be mistaken for JPEG data by 'file' command, so we ensure we try other formats first before falling back to this
	confidenceAdjust = () => 25;	// Adjust confidence so it's above fileSize matches, since being an image many things can convert with the same tools
	untouched        = dexState => dexState.meta.width && dexState.meta.height && (!dexState.meta?.driOffset || (dexState.meta?.driCount || 0)>0);	// see note below in pre() about the dirOffset/driCount check
	verifyUntouched  = dexState => dexState.meta.format!=="JPEG";
	metaProvider     = ["image", "jpeg_exif_dump"];
	pre              = async dexState =>
	{
		// some JPEG files specify a DRI (Define Restart Interval) which is a 16-bit value that specifies the number of MCUs between restart markers
		// however some are lying and don't actually have restart markers, so we modify those with a DRI count of 0 to ensure the file is processed correctly (samples: 1051.jpg and 1198.jpeg from )
		if(!dexState.meta?.driOffset || (dexState.meta?.driCount || 0)>0 || dexState.f.input.size>xu.MB*25)
			return;
		
		const rawBytes = await Deno.readFile(dexState.f.input.absolute);
		rawBytes.setUInt16BE(dexState.meta.driOffset+4, 0);
		await Deno.writeFile(dexState.f.input.absolute, rawBytes);

		dexState.meta.mustConvert = true;
	};
	converters = dexState =>
	{
		const r = [];
		if(dexState.meta.mustConvert)
		{
			r.push("convert");
			delete dexState.meta.mustConvert;
		}

		if(dexState.hasMagics("Macintosh JPEG bitmap (MacBinary)"))
			r.push("deark[module:macbinary][mac][deleteADF][convertAsExt:.jpg]");
		r.push("iconvert", "iio2png");

		// some jpgs are corrupt (image5.jpg, mpfeif07.jpg, ring_mo4.jpg) but these programs can handle it. 'canvas5' yields static garbage, don't use that.
		r.push("imageAlchemy", "pv[matchType:magic]", "noesis[type:image][matchType:magic]", "photoDraw[matchType:magic][hasExtMatch]");	// photoDraw takes like 20 seconds on average, which is a long time if allowed to run on thousands of app-specific file non-jpg that happens to have the extension or magic only
		return r;
	};
}
