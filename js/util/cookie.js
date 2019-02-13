function decodeCookie(cookies) {
    let record = {};
    for (let row of cookies.split(";").filter(e => e.trim().length)) {
        const [, encodedName, encodedVal] = /^([^=]+)=(.*)$/.exec(row);
        const name = decodeURIComponent(encodedName).trim(), val = decodeURIComponent(encodedVal);
        record[name] = val;
    }
    return record;
}

export { decodeCookie };