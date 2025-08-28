import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate the request body
    if (!body.dataPreferences || !body.securitySettings) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }

    // Here you would typically:
    // 1. Validate the user is authenticated
    // 2. Save the data to your database
    // 3. Apply security settings (e.g., enable 2FA)

    console.log('Received privacy & security preferences:', body);

    // Example: Save to database (replace with your actual database logic)
    // await savePrivacySecurityPreferences(userId, body);

    // Example: Apply security settings
    // if (body.securitySettings.twoFactorAuth) {
    //   await enableTwoFactorAuth(userId);
    // }

    return NextResponse.json(
      {
        message: 'Privacy and security preferences saved successfully',
        data: body,
      },
      { status: 200 },
    );
  } catch (error) {
    console.error('Error saving privacy and security preferences:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET() {
  try {
    // Here you would typically fetch the user's current privacy and security preferences
    // from your database

    // Example response structure
    const preferences = {
      dataPreferences: {
        allowProductUpdates: true,
        allowAnonymizedData: false,
      },
      securitySettings: {
        twoFactorAuth: false,
        sessionTimeout: true,
        loginNotifications: true,
      },
    };

    return NextResponse.json(preferences);
  } catch (error) {
    console.error('Error fetching privacy and security preferences:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
