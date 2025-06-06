import {Format} from "../../Format.js";

export class kodakKDC extends Format
{
	name         = "Kodak RAW KDC";
	website      = "http://fileformats.archiveteam.org/wiki/Kodak";
	ext          = [".kdc"];
	magic        = ["Kodak Digital Camera RAW image (DC serie)", "Kodak Digital Camera RAW image (EasyShare serie)", "image/x-kodak-kdc", "Kodak DC120 Digital Camera :kdc:"];
	mimeType     = "image/x-kodak-kdc";
	metaProvider = ["darkTable"];
	converters   = ["darktable_cli", `abydosconvert[format:${this.mimeType}]`, "nconvert[format:kdc]"];
}
