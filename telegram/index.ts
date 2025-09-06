import { Telegraf, Markup } from "telegraf";
import { MaybeInaccessibleMessage, ReactionType } from "telegraf/typings/core/types/typegram";
import { ExtraReplyMessage } from "telegraf/typings/telegram-types";

const bot = new Telegraf(process.env.BOT_TOKEN as string);

global.needed = [];

const buttonsReaction = Markup.inlineKeyboard([
    Markup.button.callback('✅', 'OK')
  ]);


const WAIT_TIME = 1000;

async function sendMessage(
  ctx: any,
  text: string,
  button?: ExtraReplyMessage
) {
  if(button) {
    await ctx.telegram.sendMessage(ctx.message.chat.id, text, button);
  } else {
    await ctx.telegram.sendMessage(ctx.message.chat.id, text);
  }
  await new Promise((resolve) => setTimeout(resolve, WAIT_TIME));
}

bot.command('need', async (ctx) => {
    const newNeeded = ctx.message.text.split("\n");
    newNeeded.slice(1).forEach(async need => {
        await sendMessage(ctx, need);
        global.needed.push(need);
    });
 });

 bot.command('list', async (ctx) => {
    if (global.needed.length === 0) {
        await sendMessage(ctx, "Il n'y a aucun élément dans la liste de course.")
    }
    let message = 'À acheter :'
    global.needed.forEach(need => {
        message = `${message}\n  - ${need}`;
    });
    await sendMessage(ctx, message);
});
    

bot.command('done', async (ctx) => {
    global.needed.forEach(async need => {
        await sendMessage(ctx, need, buttonsReaction)
    })});

bot.action('OK', (ctx, next) => {
    if (ctx.update.callback_query.message && !("text" in ctx.update.callback_query.message)) {
        return next();
    }
    const itemFound: string = ctx.update.callback_query.message?.text ?? '' ;
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
	.then(() => {
          setTimeout(() => { }, WAIT_TIME);
        });
})
 
bot.launch();
