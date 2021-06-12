"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website        : "https://www.libreoffice.org",
	gentooPackage  : "app-office/libreoffice",
	gentooUseFlags : "branding cups dbus gtk mariadb",
	unsafe         : true,
	flags          :
	{
		sofficeType : `Which format to transform into ("svg", "csv", "pdf", "png", etc). Default is "png" for images or "pdf" for everything else.`
	}
};

exports.qemu = () => "soffice";
exports.args = (state, p, r, inPath=state.input.filePath) => (["--headless", "--convert-to", (r.flags.sofficeType || (state.id.family==="image" ? "png" : "pdf")), "--outdir", "/out", inPath]);
exports.qemuData = (state, p, r) => ({osid : "gentoo", inFilePaths : [r.args.last()]});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, `in.${(r.flags.sofficeType || (state.id.family==="image" ? "png" : "pdf"))}`),
	path.join(state.output.absolute, `${state.input.name}.${(r.flags.sofficeType || (state.id.family==="image" ? "png" : "pdf"))}`))(state, p, cb);
