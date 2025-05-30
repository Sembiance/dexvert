import {Format} from "../../Format.js";

export class drHalo extends Format
{
	name           = "Dr. Halo";
	website        = "http://fileformats.archiveteam.org/wiki/Dr._Halo";
	ext            = [".cut", ".pal", ".pic"];
	magic          = ["Dr. Halo device dependent bitmap", "Dr. Halo Palette", "deark: drhalo", /^fmt\/1186( |$)/];
	idMeta         = ({macFileType}) => macFileType==="Halo";
	forbidExtMatch = [".pal", ".pic"];
	mimeType       = "application/dr-halo";
	priority       = this.PRIORITY.LOW;
	
	auxFiles = (input, otherFiles) =>
	{
		const ourExt = input.ext.toLowerCase();

		// .pal must have a corresponding .cut/.pic file
		if(ourExt===".pal")
			return otherFiles.filter(otherFile => [".cut", ".pic"].map(ext => input.name.toLowerCase() + ext).includes(otherFile.base.toLowerCase()));

		// .cut/.pic can convert on it's own, but optionally uses a .pal
		const otherFile = otherFiles.find(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.pal`);
		return otherFile ? [otherFile] : false;
	};

	converters   = r => [
		`deark[module:drhalocut]${r.f.aux ? `[file2:${r.f.aux.base}]` : ""}`, `deark[module:drhalopic]${r.f.aux ? `[file2:${r.f.aux.base}]` : ""}`,
		"convert", "recoil2png", `abydosconvert[format:${this.mimeType}]`, "hiJaakExpress[matchType:magic]", "pv[matchType:magic]"];	// pv can produce very dark, nearly black images (KLINGON.CUT)
	metaProvider = ["image"];
	weakMagic    = true;

	untouched       = ({f}) => f.input.ext.toLowerCase()===".pal";
	verifyUntouched = false;

	// Due to not having a good magic, we reject any created images less than 2 colors
	verify = ({meta}) => meta.colorCount>1;
}
