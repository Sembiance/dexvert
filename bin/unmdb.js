import {xu} from "xu";
import {runUtil, fileUtil, cmdUtil} from "xutil";
import {path, base64Decode} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Extracts data from <input.mdb> MS Access DB to <outputDirPath>",
	args :
	[
		{argid : "inputFilePath", desc : "Input MDB file to parse", required : true},
		{argid : "outputDirPath", desc : "Output dir to write to", required : true}
	]});

const schema = {};
const {stdout : schemaRaw} = await runUtil.run("mdb-schema", [argv.inputFilePath]);
let tableNameWip = null;
schemaRaw.split("\n").forEach(line =>
{
	if(line.trim().length===0)
		return;

	if(tableNameWip)
	{
		if(line.trim()===");")
		{
			tableNameWip = null;
			return;
		}

		const columnProps = (line.match(/\s*\[(?<colName>[^\]]+)]\s*(?<colType>[^,]+),?/i) || {groups : {}})?.groups;
		if(columnProps.colName)
		{
			schema[tableNameWip][columnProps.colName] = columnProps.colType;
			return;
		}
	}

	const createTableProps = (line.match(/\s*create table\s+\[(?<tableName>[^\]]+)]/i) || {groups : {}})?.groups;
	if(createTableProps.tableName)
	{
		tableNameWip = createTableProps.tableName;
		schema[tableNameWip] = {};
	}
});

await Object.entries(schema).parallelMap(async ([tableName, tableSchema]) =>
{
	const {stdout : tableData} = await runUtil.run("mdb-json", [argv.inputFilePath, tableName]);
	const tableRows = tableData.split("\n").map(v => v.trim()).filter(v => !!v).map(tableRowRaw => xu.parseJSON(tableRowRaw, {})).filter(v => !!v);

	let hasBinary = false;
	const binaryOutDir = path.join(argv.outputDirPath, tableName);
	await Deno.mkdir(binaryOutDir);

	await Object.keys(tableSchema).parallelMap(async colName =>
	{
		await tableRows.parallelMap(async (tableRow, rowNum) =>
		{
			if(!Object.isObject(tableRow[colName]) || !Object.hasOwn(tableRow[colName], "$binary"))
				return;

			hasBinary = true;

			const rowColDataFilePath = path.join(binaryOutDir, `${rowNum.toString().padStart(tableRows.length.toString().length, "0")}_${colName}`);
			await Deno.writeFile(rowColDataFilePath, base64Decode(tableRow[colName].$binary));
			tableRow[colName] = `BINARY_FILE:${path.relative(argv.outputDirPath, rowColDataFilePath)}`;
		});
	});

	if(!hasBinary)
		await fileUtil.unlink(binaryOutDir);
		
	const tableOutputData = {schema : tableSchema, data : tableRows};
	await Deno.writeTextFile(path.join(argv.outputDirPath, `${tableName}.json`), JSON.stringify(tableOutputData));
});
