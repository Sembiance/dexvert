import {Format} from "../../Format.js";

export class pixfolioCatalog extends Format
{
	name       = "Pixfolio Catalog";
	website    = "http://fileformats.archiveteam.org/wiki/PixFolio_catalog";
	ext        = [".cat", ".cix"];
	magic      = ["deark: pixfolio"];
	auxFiles   = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===`${input.name.toLowerCase()}.${input.ext===".cat" ? "cix" : "cat"}`);
	untouched  = ({f}) => f.input.ext.toLowerCase()===".cix";
	converters = ["deark[module:pixfolio][opt:pixfolio:undelete]"];
}
