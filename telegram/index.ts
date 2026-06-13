import { Telegraf, Markup } from "telegraf";
import type { ReactionType } from "telegraf/types";
import * as fs from "fs";
import * as path from "path";

const bot = new Telegraf(process.env.BOT_TOKEN as string);

global.needed = [];

const buttonsReaction = Markup.inlineKeyboard([
    Markup.button.callback('✅', 'OK')
  ])

bot.command('need', async (ctx) => {
    const newNeeded = ctx.message.text.split("\n");
    newNeeded.slice(1).forEach(async need => {
        await ctx.telegram.sendMessage(ctx.message.chat.id, need);
        global.needed.push(need);
    });
 });

 bot.command('list', async (ctx) => {
    if (global.needed.length === 0) {
        await ctx.telegram.sendMessage(ctx.message.chat.id, "Il n'y a aucun élément dans la liste de course.")
    }
    let message = 'À acheter :'
    global.needed.forEach(need => {
        message = `${message}\n  - ${need}`;
    });
    await ctx.telegram.sendMessage(ctx.message.chat.id, message);
});
    

bot.command('done', async (ctx) => {
    global.needed.forEach(async need => {
        await ctx.telegram.sendMessage(ctx.message.chat.id, need, buttonsReaction)
    })});

bot.action('OK', (ctx, next) => {

    const message = ctx.update.callback_query?.message;
    if (!message || !("text" in message)) {
        return next();
    }
    
    const itemFound: string = message.text ?? '';
    if (!itemFound || itemFound === '') return;
    
    if (!itemFound || itemFound === '') return;
    const index = global.needed.indexOf(itemFound, 0);
    if (index > -1) {
        global.needed.splice(index, 1);
    }
    const reaction: ReactionType[] = [{ type: 'emoji', emoji: '👍' }];
    if (ctx.update.callback_query.message && !("chat" in ctx.update.callback_query.message)) {
        return next();
    }
    bot.telegram.setMessageReaction(ctx.update.callback_query.message?.chat.id as number, ctx.update.callback_query.message?.message_id as number, reaction)
})
 

// Load needed items from file
const loadGroceries = () => {
    const filePath = process.env.CERBINOU_GROCERIES_LIST_FILE ?? '/data/list.txt';
    try {
        if (fs.existsSync(filePath)) {
            const content = fs.readFileSync(filePath, 'utf-8');
            global.needed = content.split('\n').filter(line => line.trim() !== '');
        } else {
            global.needed = [];
        }
    } catch (error) {
        console.error('Error loading ', filePath, error);
        global.needed = [];
    }
};

const saveGroceries = () => {
    const filePath = process.env.CERBINOU_GROCERIES_LIST_FILE ?? '/data/list.txt';
    try {
        fs.writeFileSync(filePath, global.needed.join('\n'), 'utf-8');
    } catch (error) {
        console.error('Error saving list.txt:', error);
    }
};

loadGroceries();
try {
    process.once('SIGINT', () => bot.stop('SIGINT'));
    process.once('SIGTERM', () => bot.stop('SIGTERM'));
    bot.launch();
    saveGroceries();
    bot.stop('SIGTERM');
} catch (error) {
    console.error('Bot launch error:', error);
    saveGroceries();
    try {
        bot.stop('SIGINT');
    } catch (stopError) {
        console.error('Bot cannot be stopped, it may have not run at first');
    }
    throw error
}
