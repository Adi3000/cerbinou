import { Telegraf, Markup } from "telegraf";

const bot = new Telegraf(process.env.BOT_TOKEN);

global.needed = ['carotte', 'banane'];

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
    const itemFound: string = ctx.update.callback_query.message?.text || '' ;
    if (!itemFound || itemFound === '') return;
    const index = global.needed.indexOf(itemFound, 0);
    if (index > -1) {
        global.needed.splice(index, 1);
    }
    const reaction = [{ type: 'emoji', emoji: '👍' }];
    bot.telegram.setMessageReaction(ctx.update.callback_query.message?.chat.id, ctx.update.callback_query.message?.message_id, reaction)
})
 
bot.launch();