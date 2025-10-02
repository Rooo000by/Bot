import discord
from discord import app_commands
from discord.ext import commands
import os

# ---------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN") or "MTQyMzI5Nzc2NjU4MjY1Mjk1OA.GI-lwI.KifEzYYV3LUzLmDI0ccg8jfNUzGZuU-KM5X3oQ"
1422896587146792990 = YOUR_1422896587146792990  # optional: use for faster command registration
# ---------------------

intents = discord.Intents.default()
intents.members = True  # Needed to fetch members

bot = commands.Bot(command_prefix="!", intents=intents)

# Helper to build audit log reason
def format_reason(reason: str | None, moderator: discord.Member) -> str:
    return f"{reason} (Actioned by {moderator} / ID: {moderator.id})" if reason else f"No reason provided (Actioned by {moderator} / ID: {moderator.id})"


@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=1422896587146792990)) if 1422896587146792990 else await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@bot.tree.command(name="ban", description="Ban a member from the server.", guild=discord.Object(id=1422896587146792990) if 1422896587146792990 else None)
@app_commands.describe(member="The member to ban", reason="Reason for the ban (optional)")
@app_commands.checks.has_permissions(ban_members=True)
async def ban_user(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    author = interaction.user
    guild = interaction.guild

    if member == author:
        return await interaction.response.send_message("❌ You can't ban yourself.", ephemeral=True)

    if member == guild.owner:
        return await interaction.response.send_message("❌ You can't ban the server owner.", ephemeral=True)

    # Role hierarchy check
    if author != guild.owner and author.top_role <= member.top_role:
        return await interaction.response.send_message("❌ You can't ban someone with an equal or higher role.", ephemeral=True)

    # Bot role hierarchy check
    me = guild.me
    if me.top_role <= member.top_role:
        return await interaction.response.send_message("❌ I can't ban that user due to role hierarchy.", ephemeral=True)

    audit_reason = format_reason(reason, author)

    try:
        await guild.ban(user=member, reason=audit_reason, delete_message_days=0)
    except discord.Forbidden:
        return await interaction.response.send_message("❌ I don't have permission to ban that user.", ephemeral=True)
    except discord.HTTPException as e:
        return await interaction.response.send_message(f"❌ Failed to ban user. Error: {e}", ephemeral=True)

    # Try to DM the banned user
    try:
        dm_text = (
            f"You have been **banned** from **{guild.name}**.\n"
            f"Moderator: {author} (ID: {author.id})\n"
            f"Reason: {reason if reason else 'No reason provided.'}"
        )
        await member.send(dm_text)
    except Exception:
        pass  # DM failure is not fatal

    # DM the executor
    try:
        confirm_text = (
            f"You have successfully banned **{member}** (ID: {member.id}) from **{guild.name}**.\n"
            f"Reason: {reason if reason else 'No reason provided.'}"
        )
        await author.send(confirm_text)
    except Exception:
        await interaction.followup.send("✅ Banned, but I couldn't DM you the confirmation.", ephemeral=True)

    await interaction.response.send_message(f"✅ **{member}** has been banned. Reason: {reason or 'No reason provided.'}", ephemeral=True)


# Error handler for missing permissions
@ban_user.error
async def ban_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ An error occurred: {error}", ephemeral=True)


if __name__ == "__main__":
    if TOKEN == "MTQyMzI5Nzc2NjU4MjY1Mjk1OA.GI-lwI.KifEzYYV3LUzLmDI0ccg8jfNUzGZuU-KM5X3oQ":
        print("⚠️ Replace the token or use the DISCORD_BOT_TOKEN environment variable.")
    bot.run(TOKEN)
@bot.tree.command(name="start", description="Start the bot or check if it's working.")
async def start_command(interaction: discord.Interaction):
    user = interaction.user
    await interaction.response.send_message(
        f"👋 Hello, {user.mention}! The bot is online and ready to go.",
        ephemeral=True
    )
