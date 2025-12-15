import { Linking } from 'react-native';

export async function openYouTube(videoIdOrUrl) {
  const id = videoIdOrUrl.includes('youtube.com')
    ? new URL(videoIdOrUrl).searchParams.get('v')
    : videoIdOrUrl;
  const appUrl = `youtube://www.youtube.com/watch?v=${id}`;
  const webUrl = `https://www.youtube.com/watch?v=${id}`;

  const supported = await Linking.canOpenURL(appUrl);
  if (supported) return Linking.openURL(appUrl);
  return Linking.openURL(webUrl);
}
