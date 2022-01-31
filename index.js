import {parseFeed} from 'htmlparser2';

const url = "https://www.cdc.gov.tw/RSS/RssXml/Hh094B49-DRwe2RR4eFfrQ?type=1"
const tg = "https://api.telegram.org/bot" + tgtoken + "/sendMessage"

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})

async function gatherResponse(response) {
    const {headers} = response
    const contentType = headers.get("content-type") || ""
    if (contentType.includes("application/json")) {
        return await response.json()
    } else if (contentType.includes("application/text")) {
        return response.text()
    } else if (contentType.includes("text/html")) {
        return response.text()
    } else {
        return response.text()
    }
}

/**
 * Respond with hello worker text
 * @param {Request} request
 */
async function handleRequest(request) {
    const init = {method: "GET"}
    const response = await fetch(url, init)
    if (response.status !== 200) {
        return new Response(
            JSON.stringify({
                status: "false",
                text: "resp status not expected"
            }, null, 2), {
                headers: {
                    "content-type": "application/json"
                }
            })
    }
    const content = await response.text();
    const entries = parseFeed(content);

    for (const entry of entries.items) {
        let value = await taiwancdc.get(entry.link)
        let firstRun = await taiwancdc.get("first")
        if (value === null && firstRun === "true") {
            let post = "🗞 " + entry.title + "\n\n"
            post += entry.description.replace(/<\/?[^>]+(>|$)/g, "");
            post += "\n\n"
            post += "📅 " + entry.id

            const keyboard = {
                inline_keyboard: [[
                    {
                        text: "🔗 原文網址",
                        url: entry.link
                    }
                ]]
            }
            let payload = {
                chat_id: -1001224810715,
                text: post,
                reply_markup: keyboard
            }
            const init = {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            }
            if (firstRun === "true") {
                taiwancdc.put(entry.link, 1, {expirationTtl: 604800})
                return new Response(
                    JSON.stringify({
                        status: "true",
                        text: "setted firstRun"
                    }, null, 2), {
                        headers: {
                            "content-type": "application/json"
                        }
                    })
            } else {
                let resp = await fetch(tg, init)
                // let result = await gatherResponse(resp)
                if (resp.status === 200) {
                    taiwancdc.put(entry.link, 1, {expirationTtl: 604800})
                }
            }
        }
    }
    return new Response(
        JSON.stringify({
            status: "true",
            text: "ok"
        }, null, 2), {
            headers: {
                "content-type": "application/json"
            }
        })
}
